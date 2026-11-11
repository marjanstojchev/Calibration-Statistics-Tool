from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
import os
import shutil
from typing import Any, Optional, Tuple

import yaml

from api.session import NO_DATA_MESSAGE, Session, engine, exclusive, get_session, safe_filename

router = APIRouter()

NO_LIMITS_MESSAGE = "No limits computed. Call POST /api/limits/compute first."

# Config files a session may replace by upload; the name is the part of the URL
_CONFIG_FILES = {
    "burn_in_limits": "burnInLimitsFilePath",
    "cal_limits": "calLimitsFilePath",
    "burn_in_groups": "burnInLimGroupsFilePath",
    "cal_groups": "calLimGroupsFilePath",
}
_MAX_CONFIG_BYTES = 5 * 1024 * 1024


class ComputeStatsRequest(BaseModel):
    """Limits type and parsing options. The limit/group YAML files are the ones of this session."""
    limits_type: str = "burn_in"          # "burn_in" or "calibration"
    extend_input_limits: bool = False
    extend_limits_groups: bool = False
    burn_in_cal_mode: Optional[int] = None        # 0 = auto-detect, 1 = force BurnIn, 2 = force Calibration
    include_burn_in_start: Optional[bool] = None  # None = the options chosen in the Protocols tab


def _row_to_dict(row) -> dict:
    return {
        "index":       row.index,
        "limitName":   row.limitName,
        "protType":    row.protType,
        "lowerLimit":  row.lowerLimit,
        "upperLimit":  row.upperLimit,
        "mean":        row.mean,
        "min":         row.min,
        "max":         row.max,
        "stDev":       row.stDev,
        "maxDev":      row.maxDev,
        "cg":          row.cg,
        "error":       row.error,
    }


def _group_to_dict(group) -> dict:
    return {
        "name":     group.name,
        "protType": group.protType,
        "rows":     group.limitsRowMatchDictList,
    }


def _computed(session: Session) -> Tuple[Any, str]:
    """Controller and limits type of the last finished computation of this session."""
    result = session.state.get("limits")
    if result is None:
        raise HTTPException(status_code=422, detail=NO_LIMITS_MESSAGE)
    return result["controller"], result["limits_type"]


@router.post("/compute")
def compute_stats(request: ComputeStatsRequest, session: Session = Depends(get_session)):
    """Parse the uploaded protocols against the limits files and compute full statistics.

    Flow: parse_protocol_limits → build_limits_groups → build_limits_rows →
    compute_limits_stats.  The result is stored in the session and readable via
    GET /rows and GET /groups. A new computation replaces the old one only once
    it has finished.
    """
    if request.limits_type not in ("burn_in", "calibration"):
        raise HTTPException(status_code=400, detail="limits_type must be 'burn_in' or 'calibration'.")

    with engine(session, "limits"):
        if not session.protocol_paths:
            raise HTTPException(status_code=422, detail=NO_DATA_MESSAGE)

        from shared.parse_controller import ParseController

        is_burn_in = request.limits_type == "burn_in"
        limits_path = session.config_file("burnInLimitsFilePath" if is_burn_in else "calLimitsFilePath")
        groups_path = session.config_file("burnInLimGroupsFilePath" if is_burn_in else "calLimGroupsFilePath")

        options = session.state.get("protocol_options", {})
        cal_mode = request.burn_in_cal_mode
        if cal_mode is None:
            cal_mode = options.get("burn_in_cal_mode", 0)
        include_start = request.include_burn_in_start
        if include_start is None:
            include_start = options.get("include_burn_in_start", False)

        controller = ParseController()
        controller.protToBeParsedDict["protocolPathTypeDictList"] = controller.build_prot_path_type_list(
            session.protocol_paths, cal_mode, include_start,
        )
        controller.parse_protocol_limits(
            burn_in_limits_path=limits_path,
            cal_limits_path=limits_path,
            include_burn_in=is_burn_in,
            include_cal=not is_burn_in,
            extend_burn_in=request.extend_input_limits,
            extend_cal=request.extend_input_limits,
        )
        controller.build_limits_groups(
            burn_in_lim_groups_path=groups_path,
            cal_lim_groups_path=groups_path,
            include_burn_in=is_burn_in,
            include_cal=not is_burn_in,
            extend_burn_in_groups=request.extend_limits_groups,
            extend_cal_groups=request.extend_limits_groups,
        )
        controller.build_limits_rows()
        controller.compute_limits_stats()

        session.state["limits"] = {"controller": controller, "limits_type": request.limits_type}

        protocols_used = len(controller.protToBeParsedDict["protocolPathTypeDictList"])
        row_count = len(controller.limitsRowListDict["limitsRowList"])

    return {
        "status": "ok",
        "limits_type": request.limits_type,
        "protocols_used": protocols_used,
        "row_count": row_count,
    }


@router.get("/rows")
def get_rows(session: Session = Depends(get_session)):
    """Return all computed limit rows with statistics.

    Must call POST /compute first.
    """
    controller, limits_type = _computed(session)
    rows = controller.limitsRowListDict["limitsRowList"]
    return {
        "limits_type": limits_type,
        "row_count": len(rows),
        "rows": [_row_to_dict(r) for r in rows],
    }


@router.get("/groups")
def get_groups(session: Session = Depends(get_session)):
    """Return all limits groups (with their member rows).

    Must call POST /compute first.
    """
    controller, limits_type = _computed(session)
    if limits_type == "burn_in":
        groups = controller.burnInLimitsGroupDict.get("limitsGroupList", [])
    else:
        groups = controller.calLimitsGroupDict.get("limitsGroupList", [])

    return {
        "limits_type": limits_type,
        "group_count": len(groups),
        "groups": [_group_to_dict(g) for g in groups],
    }


@router.delete("/clear")
def clear_limits(session: Session = Depends(get_session)):
    """Clear all computed limits statistics of this session.

    Equivalent to the 'Clear Statistics Data' button in the Statistics tab.
    This resets the controller state but does NOT clear the uploaded protocols.
    """
    with exclusive(session, "limits"):
        session.state.pop("limits", None)
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
# Per-session limit / group files
# ---------------------------------------------------------------------------

@router.post("/config/{name}")
async def upload_config(name: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    """Replace one of the session's limit or group YAML files (name: burn_in_limits,
    cal_limits, burn_in_groups, cal_groups). Other sessions are not affected."""
    if name not in _CONFIG_FILES:
        raise HTTPException(status_code=404, detail=f"Unknown config file. Use one of: {', '.join(_CONFIG_FILES)}")

    content = await file.read(_MAX_CONFIG_BYTES + 1)
    if len(content) > _MAX_CONFIG_BYTES:
        raise HTTPException(status_code=413, detail="Config file is too large.")
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"Not a valid YAML file: {exc}")
    if not isinstance(parsed, (dict, list)):
        raise HTTPException(status_code=400, detail="The YAML file is empty or has no content.")

    with exclusive(session, "limits_config"):
        path = session.config_file(_CONFIG_FILES[name])
        with open(path, "wb") as out:
            out.write(content)
        session.state.pop("limits", None)
    return {"status": "uploaded", "name": name, "bytes": len(content)}


@router.delete("/config")
def reset_config(session: Session = Depends(get_session)):
    """Restore the default limit and group files of this session."""
    import user_paths as up

    with exclusive(session, "limits_config"):
        for attr in _CONFIG_FILES.values():
            path = session.config_file(attr)
            shutil.copy2(os.path.join(up.config_dir, os.path.basename(path)), path)
        session.state.pop("limits", None)
    return {"status": "reset"}


# ---------------------------------------------------------------------------
# Additional statistics features
# ---------------------------------------------------------------------------


class SaveGroupRequest(BaseModel):
    """Request to create and save a new limits group."""
    group_name: str
    limits_type: str = "burn_in"  # "burn_in" or "calibration"
    limit_names: list[str]        # List of limit names to include
    match_type: str = "ExactMatch"  # "ExactMatch" or "Contains"
    save_to_yaml: bool = True


@router.post("/groups/save")
def save_limits_group(request: SaveGroupRequest, session: Session = Depends(get_session)):
    """Create a new limits group and optionally persist it to this session's groups YAML.

    Equivalent to the 'Save Group' dialog in the Statistics tab.
    """
    # Lazy-load to avoid Qt initialization at module import
    from shared.parseProtocols import LimitsGroup, ParseInputLimitsGroups

    with exclusive(session, "limits_groups"):
        controller, _ = _computed(session)

        new_group = LimitsGroup()
        new_group.name = request.group_name
        new_group.protType = "BurnIn" if request.limits_type == "burn_in" else "Calibration"

        rows = controller.limitsRowListDict.get("limitsRowList", [])
        for limit_name in request.limit_names:
            for row_obj in rows:
                if row_obj.protType != new_group.protType:
                    continue

                if request.match_type == "Contains":
                    if limit_name in row_obj.limitName:
                        new_group.limitsRowMatchDictList.append({"row": row_obj, "match": request.match_type})
                else:  # ExactMatch
                    if row_obj.limitName == limit_name:
                        new_group.limitsRowMatchDictList.append({"row": row_obj, "match": request.match_type})
                        break

        if not new_group.limitsRowMatchDictList:
            raise HTTPException(status_code=400, detail="No valid limits found matching the provided names.")

        # Persist first so a failing YAML write does not leave a half-added group in memory
        saved_to_yaml = False
        if request.save_to_yaml:
            parser = ParseInputLimitsGroups()
            if request.limits_type == "burn_in":
                yaml_path = session.config_file("burnInLimGroupsFilePath")
                parser.loadBurnInInputLimitsGroupsDictYAML(yaml_path)
                if parser.burnInErrorStatus == 1:
                    raise HTTPException(status_code=500, detail="Failed to load the BurnIn limits groups file.")
                parser.saveToActualBurnInLimitsGroupsDict(new_group, alreadyExtended=0)
                parser.saveLimitsGroupsDictYAML(parser.burnInInputLimitsGroupsDict, yaml_path)
            else:
                yaml_path = session.config_file("calLimGroupsFilePath")
                parser.loadCalInputLimitsGroupsDictYAML(yaml_path)
                if parser.calErrorStatus == 1:
                    raise HTTPException(status_code=500, detail="Failed to load the Calibration limits groups file.")
                parser.saveToActualCalLimitsGroupsDict(new_group, alreadyExtended=0)
                parser.saveLimitsGroupsDictYAML(parser.calInputLimitsGroupsDict, yaml_path)
            saved_to_yaml = True

        grp_dict = (
            controller.burnInLimitsGroupDict
            if request.limits_type == "burn_in"
            else controller.calLimitsGroupDict
        )
        grp_dict["limitsGroupList"].append(new_group)
        grp_dict["activeGroupIndex"] = len(grp_dict["limitsGroupList"]) - 1

    return {
        "status": "saved",
        "group_name": new_group.name,
        "limits_count": len(new_group.limitsRowMatchDictList),
        "saved_to_session_file": saved_to_yaml,
    }


@router.get("/series/{limit_name}")
def get_statistical_series(limit_name: str, limits_type: str = "burn_in", session: Session = Depends(get_session)):
    """Get histogram data for a specific limit (statistical series).

    Returns the raw values and computed bins for visualization.
    Equivalent to the 'Statistical Series' button in Qt GUI.
    """
    controller, _ = _computed(session)

    rows = controller.limitsRowListDict.get("limitsRowList", [])
    target_row = None
    for row in rows:
        if row.limitName == limit_name and row.protType == ("BurnIn" if limits_type == "burn_in" else "Calibration"):
            target_row = row
            break

    if target_row is None:
        raise HTTPException(status_code=404, detail=f"Limit '{limit_name}' not found.")

    # Collect plot data (same logic as _collect_plot_data in stats_handlers.py)
    parsed_dict = (
        controller.burnInParsedProtDict
        if limits_type == "burn_in"
        else controller.calParsedProtDict
    )
    parsed_list = parsed_dict.get("parsedDataList", [])

    values = []
    protocol_indices = []
    for idx, parsed_data in enumerate(parsed_list):
        for diag_idx, diagram_dict in enumerate(parsed_data.diagrams):
            for param_name, param_obj in diagram_dict.items():
                if hasattr(param_obj, limit_name):
                    val = getattr(param_obj, limit_name)
                    if val is not None:
                        values.append(float(val))
                        protocol_indices.append(idx)

    if not values:
        raise HTTPException(status_code=404, detail=f"No data points found for limit '{limit_name}'.")

    import math
    n = len(values)
    bin_count = max(1, min(int(math.sqrt(n)), 50))  # Sqrt rule with cap at 50 bins
    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / bin_count or 1.0

    bins = [min_val + i * bin_width for i in range(bin_count + 1)]
    hist = [0] * bin_count

    for v in values:
        bin_idx = min(int((v - min_val) / bin_width), bin_count - 1)
        hist[bin_idx] += 1

    return {
        "limit_name": limit_name,
        "limits_type": limits_type,
        "values": values,
        "protocol_indices": protocol_indices,
        "count": len(values),
        "histogram": {
            "bins": bins,
            "counts": hist,
        },
        "statistics": {
            "mean": target_row.mean,
            "min": target_row.min,
            "max": target_row.max,
            "stDev": target_row.stDev,
            "lowerLimit": target_row.lowerLimit,
            "upperLimit": target_row.upperLimit,
        },
    }


class ExportPptxRequest(BaseModel):
    """Request to export current limits table to PPTX."""
    limits_type: str = "burn_in"
    output_filename: str = "statistics_export.pptx"


@router.post("/export/pptx")
def export_limits_pptx(request: ExportPptxRequest, session: Session = Depends(get_session)):
    """Export limits table to a PPTX file in this session's statistic folder.

    Creates a PowerPoint with statistics table (similar to group PPTX export in Qt GUI).
    """
    controller, _ = _computed(session)

    from pptx import Presentation
    from pptx.util import Inches, Pt
    from datetime import datetime

    rows = controller.limitsRowListDict.get("limitsRowList", [])
    prot_type = "BurnIn" if request.limits_type == "burn_in" else "Calibration"
    filtered_rows = [r for r in rows if r.protType == prot_type]

    if not filtered_rows:
        raise HTTPException(status_code=404, detail=f"No {prot_type} limits found.")

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = f"{prot_type} Limits Statistics — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    title_frame.paragraphs[0].font.size = Pt(18)
    title_frame.paragraphs[0].font.bold = True

    rows_count = len(filtered_rows) + 1  # +1 for header
    cols_count = 10  # limitName, protType, lower, upper, mean, min, max, stDev, maxDev, cg

    table_shape = slide.shapes.add_table(
        rows_count, cols_count,
        Inches(0.3), Inches(1.0),
        Inches(9.4), Inches(5.5)
    )
    table = table_shape.table

    headers = ["Limit Name", "Type", "Lower", "Upper", "Mean", "Min", "Max", "StDev", "MaxDev", "Cg"]
    for col_idx, header in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = header
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(9)

    for row_idx, row_obj in enumerate(filtered_rows, start=1):
        values = [
            row_obj.limitName,
            row_obj.protType,
            f"{row_obj.lowerLimit:.2f}",
            f"{row_obj.upperLimit:.2f}",
            f"{row_obj.mean:.3f}",
            f"{row_obj.min:.3f}",
            f"{row_obj.max:.3f}",
            f"{row_obj.stDev:.3f}",
            f"{row_obj.maxDev:.3f}",
            f"{row_obj.cg:.2f}",
        ]
        for col_idx, val in enumerate(values):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(val)
            cell.text_frame.paragraphs[0].font.size = Pt(8)

    filename = safe_filename(request.output_filename, "statistics_export.pptx", ".pptx")
    with exclusive(session, "limits_export"):
        prs.save(os.path.join(session.output_dir("statistic"), filename))

    return {
        "status": "exported",
        "pptx_file": filename,
        "output_type": "statistic",
        "row_count": len(filtered_rows),
    }
