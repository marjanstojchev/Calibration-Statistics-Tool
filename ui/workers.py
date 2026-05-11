"""Background worker objects for long-running operations (PST-60).

Each worker is a ``QObject`` subclass that is moved to a ``QThread`` at call
site.  They must **never** touch Qt widgets directly — only emit signals.  The
connected slots on the main thread then update the UI.

Usage pattern (same for every worker)::

    worker = ParseWorker(...)
    thread = QThread()
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    worker.progress.connect(some_ui_slot)
    worker.error.connect(some_error_slot)

    thread.start()
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    import logconfig as _logcfg  # type: ignore[import]


# ---------------------------------------------------------------------------
# ParseWorker — loads and parses protocol files
# ---------------------------------------------------------------------------

class ParseWorker(QObject):
    """Load raw protocol data files for all protocols in the parse queue.

    Emits ``progress(int, str)`` updates so the UI can animate its progress
    bar without blocking.  When complete, emits ``finished`` with four lists
    required by the main-thread post-processing steps.

    Parameters
    ----------
    filtered_sys_diag_list:
        Per-protocol dict list from ``filter_protocol_file_lists``.
    filtered_tx_ant_diag_list:
        Corresponding TxAntDiag list.
    plot_setup:
        ``plotSetup`` dict (read-only during worker run).
    tx_ant_plot_setup:
        TxAntDiagrams ``plotSetup`` dict (read-only during worker run).
    protocol_path_dict:
        Full ``protToBeParsedDict`` (used to get file tail for progress label).
    prog_bar_label_str:
        Base string prepended to per-file progress labels.
    prot_to_be_parsed_list_len:
        Total protocol count (used for progress bar max).
    """

    progress: Signal = Signal(int, str)
    """Emits (bar_value: int, label_text: str) for progress bar updates."""

    finished: Signal = Signal(list, list, list, list)
    """Emits (sysDiagDataList, txAntDiagDataList,
               sysDiagParsedDataList, txAntDiagParsedDataList)."""

    error: Signal = Signal(str)
    """Emits an error message string if an exception is raised."""

    def __init__(
        self,
        filtered_sys_diag_list: list,
        filtered_tx_ant_diag_list: list,
        plot_setup: dict,
        tx_ant_plot_setup: dict,
        protocol_path_dict: dict,
        prog_bar_label_str: str,
        prot_to_be_parsed_list_len: int,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._filtered_sys_diag_list      = filtered_sys_diag_list
        self._filtered_tx_ant_diag_list   = filtered_tx_ant_diag_list
        self._plot_setup                  = plot_setup
        self._tx_ant_plot_setup           = tx_ant_plot_setup
        self._protocol_path_dict          = protocol_path_dict
        self._prog_bar_label_str          = prog_bar_label_str
        self._prot_to_be_parsed_list_len  = prot_to_be_parsed_list_len

    def run(self) -> None:
        """Entry point — called by QThread.started signal."""
        try:
            result = self._execute()
            self.finished.emit(*result)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))

    def _execute(self) -> tuple[list, list, list, list]:
        import loaddata as ld
        import load_TxAntData as ld_txantdiag

        total = self._prot_to_be_parsed_list_len
        label = self._prog_bar_label_str
        use_muster      = self._plot_setup.get("useSensorMuster", 0)
        muster_list     = self._plot_setup.get("sensorMusterList", [])
        tx_use_muster   = self._tx_ant_plot_setup.get("useSensorMuster", 0)
        tx_muster_list  = self._tx_ant_plot_setup.get("sensorMusterList", [])

        twenty_pct      = int(total / 5) if total >= 5 else 0
        twenty_pct_res  = total % 5

        sys_diag_data_list:          list = []
        tx_ant_diag_data_list:       list = []
        sys_diag_parsed_data_list:   list = []
        tx_ant_diag_parsed_data_list: list = []

        idx       = 1
        final     = 0
        set_final = False

        for proto_idx in range(total):
            # --- Sys-diag load ---
            sys_diag_per_prot = self._filtered_sys_diag_list[proto_idx]["ptu2FilesList"]
            sys_loaded = ld.LoadData(sys_diag_per_prot, use_muster, muster_list)
            if sys_loaded.invalidPath == 1:
                sys_diag_data_list.append([])
            else:
                sys_diag_data_list.append(sys_diag_per_prot)
                sys_diag_parsed_data_list += sys_loaded.parseDataList

            # --- TxAntDiag load ---
            tx_ant_per_prot = self._filtered_tx_ant_diag_list[proto_idx]["txAntDiagList"]
            tx_loaded = ld_txantdiag.LoadData(tx_ant_per_prot, tx_use_muster, tx_muster_list)
            if tx_loaded.invalidPath == 1:
                tx_ant_diag_data_list.append([])
            else:
                tx_ant_diag_data_list.append(tx_ant_per_prot)
                tx_ant_diag_parsed_data_list += tx_loaded.parseDataList

            # --- Progress emission ---
            _, tail = os.path.split(
                self._protocol_path_dict["protocolPathTypeDictList"][proto_idx]["protocolPath"]
            )
            if set_final:
                bar_val   = final
                label_txt = label + "Protocol: " + tail
            else:
                bar_val   = idx
                label_txt = label + "Protocol: " + tail

            if twenty_pct != 0 and idx % twenty_pct == 0:
                if int(idx / twenty_pct) < 5:
                    self.progress.emit(idx, label_txt)
                else:
                    set_final = True
                    final     = idx + twenty_pct_res
                    self.progress.emit(final, label_txt)
            else:
                self.progress.emit(bar_val, label_txt)

            idx += 1

        return (
            sys_diag_data_list,
            tx_ant_diag_data_list,
            sys_diag_parsed_data_list,
            tx_ant_diag_parsed_data_list,
        )


# ---------------------------------------------------------------------------
# SysDiagWorker — generates antenna system diagrams
# ---------------------------------------------------------------------------

class SysDiagWorker(QObject):
    """Run ``antSysDiag.start_data_evaluation`` off the main thread.

    Parameters
    ----------
    parsed_data_list:
        ``sysDiagParsedDataDict["parsedDataList"]``
    kwargs:
        All keyword arguments forwarded verbatim to ``start_data_evaluation``.
    """

    finished: Signal = Signal()
    error: Signal    = Signal(str)

    def __init__(
        self,
        parsed_data_list: list,
        plot_setup: Any,
        chirp_config: Any,
        graph_config: Any,
        diagram_config: Any,
        two_graph_setup_list: list,
        four_graph_setup_list: list,
        three_graph_setup_list: list,
        all_on_one_slide_graph_list: list,
        diagram_config_list: list,
        logger: Any,
        output_path: str,
        pptx_name: str,
        template_path: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._args = (
            parsed_data_list,
            plot_setup,
            chirp_config,
            graph_config,
            diagram_config,
            two_graph_setup_list,
            four_graph_setup_list,
            three_graph_setup_list,
            all_on_one_slide_graph_list,
            diagram_config_list,
            logger,
            output_path,
            pptx_name,
            template_path,
        )

    def run(self) -> None:
        try:
            import AntennaSystemDiagrams as antSysDiag  # noqa: PLC0415
            antSysDiag.start_data_evaluation(*self._args)
            self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


# ---------------------------------------------------------------------------
# TxAntDiagWorker — generates TxAnt diagrams
# ---------------------------------------------------------------------------

class TxAntDiagWorker(QObject):
    """Run ``TxAntDiagrams.start_data_evaluation`` off the main thread."""

    finished: Signal = Signal()
    error: Signal    = Signal(str)

    def __init__(
        self,
        parsed_data_list: list,
        plot_setup: Any,
        graph_config: Any,
        logger: Any,
        output_path: str,
        pptx_name: str,
        template_path: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._args = (
            parsed_data_list,
            plot_setup,
            graph_config,
            logger,
            output_path,
            pptx_name,
            template_path,
        )

    def run(self) -> None:
        try:
            import TxAntDiagrams as _mod  # noqa: PLC0415
            _mod.start_data_evaluation(*self._args)
            self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


# ---------------------------------------------------------------------------
# AntPatWorker — generates antenna pattern diagrams
# ---------------------------------------------------------------------------

class AntPatWorker(QObject):
    """Run ``antpat_v5_main_v3.start_data_evaluation`` off the main thread."""

    finished: Signal = Signal()
    error: Signal    = Signal(str)

    def __init__(
        self,
        parsed_data_list: list,
        logger: Any,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._parsed_data_list = parsed_data_list
        self._logger           = logger

    def run(self) -> None:
        try:
            import antpat_v5_main_v3 as antPat1  # noqa: PLC0415
            antPat1.start_data_evaluation(
                self._parsed_data_list,
                self._logger,
            )
            self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
