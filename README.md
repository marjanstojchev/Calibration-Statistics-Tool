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

- `main.py` - Main GUI application
- `pyside_qtgui.py` - Qt GUI components
- `statistic.py` - Statistics processing
- `antpat_v5_main_v3.py` - Antenna pattern analysis
- `TxAntDiagrams.py` - Transmit antenna diagrams
- Various data processing modules

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Lint code:
```bash
ruff check .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request