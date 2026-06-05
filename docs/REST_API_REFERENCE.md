# REST API Complete Endpoint Reference

## Overview

The Calibration Statistics Tool REST API provides full programmatic access to all desktop application features. All endpoints are organized by functional module.

**Base URL**: `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs` (interactive Swagger UI)

---

## Complete Endpoint List

### 1. Protocols (Parse & Upload)

#### `POST /api/protocols/parse`
Parse protocol files and discover PTU2/TxAntDiag measurement files.

**Request Body**:
```json
{
  "protocol_paths": ["/path/to/protocol1.txt", "/path/to/protocol2.txt"],
  "search_ptu2_files": true,
  "search_txantdiag_files": false,
  "use_error": false,
  "use_abort": true,
  "use_limits_exceeded": true,
  "latest_protocol": false
}
```

**Response**:
```json
{
  "status": "ok",
  "protocols_accepted": 4,
  "ptu2_files_loaded": 32,
  "tx_ant_diag_loaded": 0
}
```

---

#### `POST /api/protocols/upload`
Upload protocol files from client (multipart/form-data).

**Not yet implemented** – use `/parse` with server-side paths for now.

---

#### `DELETE /api/protocols/clear`
Clear all parsed data from memory (equivalent to "Clear Data" button).

**Response**:
```json
{
  "status": "cleared",
  "sys_diag_ptu2_loaded": 0,
  "tx_ant_diag_loaded": 0
}
```

---

### 2. System Diagrams (Batch PPTX Generation)

#### `GET /api/system_diagrams/config/defaults`
Get default configuration matching UI startup values.

**Response**: Full `SysDiagStartRequest` model with all defaults.

---

#### `POST /api/system_diagrams/start`
Generate system diagrams PPTX with optional configuration override.

**Request Body** (all fields optional):
```json
{
  "plot_setup": {
    "targetAngle": 1,
    "upsideDown": 0,
    "xScaleSizeAuto": 0,
    "xScaleSizeAz": 90.0,
    "xScaleSizeEl": 45.0,
    "imageDpi": 220,
    "nofSensorMeasToShow": 32
  },
  "chirp_config": {"chirp0": 1, "chirp1": 0, "chirp2": 0, "chirp3": 0},
  "graph_config": {
    "level": 1,
    "normLevel": 1,
    "phaseDiff": 1,
    "corrPhaseDiff": 1
  },
  "diagram_config": {
    "selectDiagrams": 0,
    "oddOrEven": 0,
    "lowerNumber": 0,
    "higherNumber": 4
  },
  "pptx_title": "Antenna_diagrams.pptx"
}
```

**Response**:
```json
{
  "status": "success",
  "output_path": "C:\\Users\\...\\output\\Antenna_diagrams.pptx"
}
```

---

### 3. TX Antenna Diagrams

#### `GET /api/tx_diagrams/config/defaults`
Get default TX diagrams configuration.

---

#### `POST /api/tx_diagrams/start`
Generate TX antenna diagrams PPTX.

**Request Body** (all fields optional):
```json
{
  "plot_setup": {
    "targetAngle": 0,
    "AzDiag": 1,
    "ElDiag": 1,
    "plotOrigGraphs": 1,
    "plotNormGraphs": 1,
    "graphsPerSlide": 1
  },
  "graph_config": {"level": 1},
  "pptx_title": "TxAntenna_diagrams.pptx"
}
```

**Response**:
```json
{
  "status": "success",
  "output_path": "C:\\...\\output_tx_diagrams\\TxAntenna_diagrams.pptx"
}
```

---

### 4. Antenna Patterns (YAML/JSON Generation)

#### `GET /api/antenna_patterns/config/defaults`
Get default antenna pattern configuration.

---

#### `POST /api/antenna_patterns/start`
Generate antenna pattern YAML/JSON files.

**Request Body** (all fields optional):
```json
{
  "chirp_config": {"chirp0": 1, "chirp1": 0, "chirp2": 0, "chirp3": 0},
  "ptu2_input_conf": {
    "diagTypeInfo": 1,
    "targetAngle": 1,
    "upsideDown": 0,
    "tables": [
      {
        "antenna_pattern_idx": 0,
        "patternType": 1,
        "rotationAxis": 1,
        "nofApplicableTxAnt": 1,
        "nofApplicableRxAnt": 4,
        "applTxAntInd": [0],
        "applRxAntInd": [0, 1, 2, 3],
        "gainCalcMethod": 1
      }
    ]
  },
  "output_version": 0
}
```

**Response**:
```json
{"status": "success"}
```

---

### 5. Hüllkurven (Envelope Limits Generation)

#### `GET /api/huellkurven/config/defaults`
Get default Hüllkurven configuration.

---

#### `POST /api/huellkurven/start`
Compute envelope curve limits and save DAT + PNG files.

**Request Body** (all fields optional):
```json
{
  "data_conf": {
    "AzDiag": 1,
    "ElDiag": 1,
    "minSigma": -10,
    "maxSigma": 10,
    "patternLimitsMethod": 0
  },
  "plot_setup": {
    "xScaleSizeAuto": 0,
    "xScaleSizeAz": 90.0,
    "xScaleSizeEl": 45.0
  },
  "chirp_config": {"chirp0": 1, "chirp1": 0, "chirp2": 0, "chirp3": 0}
}
```

**Response**:
```json
{
  "status": "success",
  "output_path": "C:\\...\\output_huellkurven"
}
```

---

### 6. Limits Statistics

#### `POST /api/limits/compute`
Parse limits files and compute statistics.

**Request Body**:
```json
{
  "limits_type": "burn_in",
  "input_limits_file_path": "C:\\...\\BurnInLimits.yaml",
  "extend_input_limits": false,
  "limits_groups_file_path": "C:\\...\\BurnInLimGroups.yaml",
  "extend_limits_groups": false
}
```

**Response**:
```json
{
  "status": "ok",
  "limits_type": "burn_in",
  "row_count": 42
}
```

---

#### `GET /api/limits/rows`
Get all computed limit rows with statistics (must call `/compute` first).

**Response**:
```json
{
  "limits_type": "burn_in",
  "row_count": 42,
  "rows": [
    {
      "index": 0,
      "limitName": "Temperature_Sensor1",
      "protType": "BurnIn",
      "lowerLimit": -40.0,
      "upperLimit": 85.0,
      "mean": 25.3,
      "min": 22.1,
      "max": 28.4,
      "stDev": 1.2,
      "maxDev": 3.1,
      "cg": 15.8,
      "error": {}
    }
  ]
}
```

---

#### `GET /api/limits/groups`
Get all limits groups with member rows (must call `/compute` first).

**Response**:
```json
{
  "limits_type": "burn_in",
  "group_count": 5,
  "groups": [
    {
      "name": "Temperature",
      "protType": "BurnIn",
      "rows": ["Temperature_Sensor1", "Temperature_Sensor2"]
    }
  ]
}
```

---

#### `DELETE /api/limits/clear`
Clear computed limits statistics (does NOT clear parsed protocols).

**Response**:
```json
{"status": "cleared"}
```

---

#### `POST /api/limits/groups/save`
Create and save a new limits group (equivalent to "Save Group" dialog).

**Request Body**:
```json
{
  "group_name": "MyCustomGroup",
  "limits_type": "burn_in",
  "limit_names": ["Temperature_Sensor1", "Voltage_Rail1", "Power_Supply_3V3"],
  "match_type": "ExactMatch",
  "save_to_yaml": true
}
```

**Response**:
```json
{
  "status": "saved",
  "group_name": "MyCustomGroup",
  "limits_count": 3,
  "yaml_path": "C:\\...\\BurnInLimGroups.yaml"
}
```

---

#### `GET /api/limits/series/{limit_name}?limits_type=burn_in`
Get statistical series (histogram data) for a specific limit.

**Response**:
```json
{
  "limit_name": "Temperature_Sensor1",
  "limits_type": "burn_in",
  "values": [25.3, 25.1, 25.4, ...],
  "protocol_indices": [0, 1, 2, ...],
  "count": 42,
  "histogram": {
    "bins": [22.0, 22.5, 23.0, ...],
    "counts": [2, 5, 8, ...]
  },
  "statistics": {
    "mean": 25.3,
    "min": 22.1,
    "max": 28.4,
    "stDev": 1.2,
    "lowerLimit": -40.0,
    "upperLimit": 85.0
  }
}
```

---

#### `POST /api/limits/export/pptx`
Export limits table to PowerPoint presentation.

**Request Body**:
```json
{
  "limits_type": "burn_in",
  "output_filename": "statistics_export.pptx"
}
```

**Response**:
```json
{
  "status": "exported",
  "output_path": "C:\\...\\output_statistic\\statistics_export.pptx",
  "row_count": 42
}
```

---

### 7. System Diagrams Interactive

#### `POST /api/interactive/fill`
Populate interactive table data (protocols + parameters).

**Response**:
```json
{
  "filled": true,
  "protocol_count": 4,
  "parameter_count": 256,
  "protocols": [
    {"date_time": "2024-01-15_10-15-20", "tuner": "Tuner0", "sensor": "rf12345", "label": "..."}
  ],
  "parameters": [
    {
      "antenna_type": 1,
      "graph_type": "level",
      "diagram_num": 0,
      "rx_channel": 0,
      "label": "level_AntType1_Diag0_RxCh0"
    }
  ]
}
```

---

#### `GET /api/interactive/state`
Return the last fill result without re-computing.

---

#### `DELETE /api/interactive/clear`
Clear interactive fill state.

---

### 8. Statistics & Protocol Info

#### `GET /api/stats/`
Get counts of currently loaded parsed data.

**Response**:
```json
{
  "sys_diag_ptu2_loaded": 32,
  "tx_ant_diag_loaded": 0
}
```

---

#### `DELETE /api/stats/clear`
Alias for `DELETE /api/protocols/clear` (clears parsed data).

---

### 9. Logs

#### `GET /logs/all`
Get all buffered log entries from all modules.

#### `GET /logs/{module}`
Get logs for specific module (system_diagrams, tx_diagrams, antenna_patterns, main_load_data).

---

### 10. Downloads (File Serving)

#### `GET /api/downloads/list/{output_type}`
List all files in output directory.

**Path Parameters**:
- `output_type`: `system_diagrams`, `tx_diagrams`, `antenna_patterns`, `huellkurven`, `statistic`, `certificates`, `merge`

**Response**:
```json
{
  "files": ["Antenna_diagrams.pptx", "TxAntenna_diagrams.pptx"],
  "directory": "C:\\...\\output"
}
```

---

#### `GET /api/downloads/list/{output_type}/recursive`
Recursively list all files (for nested directories like Hüllkurven).

**Response**:
```json
{
  "files": [
    {"path": "AntType1/Az_TxAnt0_Diagram0_Chirp0.dat", "size": 12345, "modified": 1234567890.0}
  ],
  "directory": "C:\\...\\output_huellkurven"
}
```

---

#### `GET /api/downloads/download/{output_type}/{filename:path}`
Download a specific file.

**Example**: `GET /api/downloads/download/system_diagrams/Antenna_diagrams.pptx`

**Returns**: File with appropriate Content-Type header.

---

#### `DELETE /api/downloads/clear/{output_type}`
Delete all files in the output directory (equivalent to "Clear" button before generation).

---

## Typical Workflow

### 1. Parse protocols
```bash
POST /api/protocols/parse
{
  "protocol_paths": ["C:\\...\\protocol1.txt"],
  "search_ptu2_files": true
}
```

### 2. Generate outputs
```bash
# System diagrams with custom config
POST /api/system_diagrams/start
{
  "chirp_config": {"chirp0": 1},
  "pptx_title": "MyDiagrams.pptx"
}

# TX diagrams with defaults
POST /api/tx_diagrams/start
{}

# Antenna patterns
POST /api/antenna_patterns/start
{}

# Hüllkurven limits
POST /api/huellkurven/start
{}
```

### 3. Compute limits statistics
```bash
POST /api/limits/compute
{
  "limits_type": "burn_in",
  "input_limits_file_path": "C:\\...\\BurnInLimits.yaml",
  "limits_groups_file_path": "C:\\...\\BurnInLimGroups.yaml"
}

GET /api/limits/rows
GET /api/limits/groups
```

### 4. Download generated files
```bash
# List available files
GET /api/downloads/list/system_diagrams

# Download PPTX
GET /api/downloads/download/system_diagrams/MyDiagrams.pptx

# List Hüllkurven files recursively
GET /api/downloads/list/huellkurven/recursive

# Download a specific DAT file
GET /api/downloads/download/huellkurven/AntType1/Az_TxAnt0_Diagram0_Chirp0.dat
```

### 5. Clear data when done
```bash
DELETE /api/protocols/clear       # Clear parsed data
DELETE /api/limits/clear          # Clear computed statistics
DELETE /api/interactive/clear      # Clear interactive state
DELETE /api/downloads/clear/system_diagrams  # Clear output files
```

---

## Configuration Flexibility

All `/start` endpoints accept **optional** configuration. Omit fields to use defaults:

```json
// Use all defaults
POST /api/system_diagrams/start
{}

// Override just chirp selection
POST /api/system_diagrams/start
{
  "chirp_config": {"chirp0": 1, "chirp1": 1}
}

// Full customization
POST /api/system_diagrams/start
{
  "plot_setup": {"imageDpi": 300, "xScaleSizeAz": 120},
  "chirp_config": {"chirp0": 1, "chirp1": 1},
  "graph_config": {"level": 1, "normLevel": 0},
  "pptx_title": "HighRes_Diagrams.pptx"
}
```

Use `GET /config/defaults` to see all available options and their defaults.

---

## Error Handling

All endpoints return standard HTTP status codes:
- **200**: Success
- **400**: Bad request (invalid parameters, file not found)
- **422**: Unprocessable entity (no parsed data, missing dependencies)
- **500**: Internal server error

Error responses include a `detail` message:
```json
{
  "detail": "No parsed data. Run /api/protocols/parse first."
}
```

---

## Web UI Considerations

### State Management
- Parsed data lives in memory (`shared.load_protocols` module attributes)
- Call `/parse` once, then generate multiple outputs without re-parsing
- Check `/api/stats/` to verify data is loaded before calling `/start` endpoints
- Clear state with `DELETE /api/protocols/clear` when switching datasets

### Configuration UX
- Fetch defaults via `GET /config/defaults` to pre-populate forms
- Only send modified fields in POST requests (all fields are optional)
- Show a "Use Defaults" button to reset forms to `/config/defaults` values

### File Management
- After calling `/start`, use `/api/downloads/list/...` to show generated files
- Provide download links using `/api/downloads/download/...` URLs
- Offer "Clear Output" button mapped to `DELETE /api/downloads/clear/...`

### Real-time Feedback
- Poll `/logs/{module}` during long-running operations for progress updates
- Or use Server-Sent Events (SSE) if implemented in logs router

---

## All Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **Protocols** |
| POST | `/api/protocols/parse` | Parse protocol files |
| DELETE | `/api/protocols/clear` | Clear parsed data |
| **System Diagrams** |
| GET | `/api/system_diagrams/config/defaults` | Get defaults |
| POST | `/api/system_diagrams/start` | Generate PPTX |
| **TX Diagrams** |
| GET | `/api/tx_diagrams/config/defaults` | Get defaults |
| POST | `/api/tx_diagrams/start` | Generate TX PPTX |
| **Antenna Patterns** |
| GET | `/api/antenna_patterns/config/defaults` | Get defaults |
| POST | `/api/antenna_patterns/start` | Generate YAML files |
| **Hüllkurven** |
| GET | `/api/huellkurven/config/defaults` | Get defaults |
| POST | `/api/huellkurven/start` | Generate envelope limits |
| **Limits** |
| POST | `/api/limits/compute` | Compute statistics |
| GET | `/api/limits/rows` | Get all limit rows |
| GET | `/api/limits/groups` | Get limit groups |
| DELETE | `/api/limits/clear` | Clear statistics |
| POST | `/api/limits/groups/save` | Save new group to YAML |
| GET | `/api/limits/series/{name}` | Get statistical series |
| POST | `/api/limits/export/pptx` | Export table to PPTX |
| **Interactive** |
| POST | `/api/interactive/fill` | Fill table data |
| GET | `/api/interactive/state` | Get current state |
| DELETE | `/api/interactive/clear` | Clear state |
| **Stats** |
| GET | `/api/stats/` | Get loaded data counts |
| DELETE | `/api/stats/clear` | Clear (alias for protocols/clear) |
| **Logs** |
| GET | `/logs/all` | Get all logs |
| GET | `/logs/{module}` | Get module logs |
| **Downloads** |
| GET | `/api/downloads/list/{type}` | List files |
| GET | `/api/downloads/list/{type}/recursive` | List files recursively |
| GET | `/api/downloads/download/{type}/{file}` | Download file |
| DELETE | `/api/downloads/clear/{type}` | Clear output directory |
| **Health** |
| GET | `/` | Health check |

Total: **35 endpoints** covering all desktop UI functionality.
