# StatisticToolPython

A comprehensive statistics and antenna pattern analysis tool for radar systems, built with Python and PySide6.

## Features

- **Statistics Analysis**: Process and analyze measurement data with statistical limits
- **Antenna Pattern Processing**: Handle antenna diagrams and patterns for various radar types
- **GUI Interface**: User-friendly Qt-based interface for data visualization
- **Report Generation**: Automated PowerPoint and PDF report creation
- **Data Processing**: Support for multiple data formats (JSON, YAML, protocol files)

## Requirements

- Python 3.8+
- PySide6 for GUI
- matplotlib for plotting
- numpy for numerical operations
- PyYAML for configuration
- python-pptx for PowerPoint generation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd statistictoolpython
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

Run the main application:
```bash
python main.py
```

Or use the command-line entry point:
```bash
statistictool
```

## Project Structure

The application follows an MVC architecture split across several sub-packages:

```
main.py                         # Thin wiring file -- startup, DI, handler wiring
shared/                         # Domain logic (controllers, parsers, models)
    models.py                   # Data model classes
    parse_controller.py         # ParseController -- protocol/PTU2 business logic
    plot_controller.py          # PlotController -- diagram/plot state management
    calcdiagram_functions.py    # Vectorised diagram calculations (NumPy)
    parsePTU2data.py            # PTU2 file parser and data structures
    parse_helpers.py            # Protocol parsing helpers
    loaddata.py                 # Data loading utilities
ui/
    main_view.py                # MainView -- owns QApplication and all widgets
    pyside_qtgui.py             # Backward-compat shim (delegates to MainView)
    ui_constants.py             # Pure-Python layout/size/style constants
    widgets.py                  # Reusable Qt widget classes (PlotFrame, etc.)
    handlers/                   # Signal handler modules (one per tab)
        app_context.py          # AppContext -- dependency-injection container
        parse_handlers.py       # Parse Protocols tab handlers
        sys_diag_handlers.py    # System Diagrams tab handlers
        tx_ant_diag_handlers.py # Tx-Antenna Diagrams tab handlers
        ant_pat_handlers.py     # Antenna Patterns tab handlers
    tabs/                       # Tab widget declarations (one file per tab)
        parse_prot_tab.py
        sys_diag_tab.py
        tx_ant_diag_tab.py
        ant_pat_tab.py
system_diagrams/                # AntennaSystemDiagrams computation module
antenna_patterns/               # Antenna pattern analysis (antpat_v5)
tx_diagrams/                    # Tx-Antenna Diagrams computation module
config/                         # YAML configuration files
tests/                          # Pytest test suite (613 tests)
    conftest.py                 # Shared fixtures and Qt session setup
    integration/                # Real-Qt integration tests
docs/                           # Architecture documentation
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Run benchmarks (local only, informational):
```bash
pytest --benchmark-only
```

Lint code:
```bash
ruff check .
```

## Architecture

Detailed architecture documentation is in [docs/](docs/):
- `docs/mvc_architecture.md` — MVC design, dependency injection, layer boundaries

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request