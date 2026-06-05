# Qt GUI → REST API Coverage Audit

## Executive Summary

**API Coverage: 90%** — All critical generation workflows are fully implemented. Minor gaps exist in GUI-specific visualization and group management features.

---

## Tab-by-Tab Analysis

### ✅ 1. Parse Protocols Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| Import protocols (directory/files) | `POST /api/protocols/parse` | ✅ Full coverage |
| Parse with PTU2/TxAntDiag | `POST /api/protocols/parse` | ✅ Full coverage |
| Configuration (burn-in/cal, EOL, abort) | `POST /api/protocols/parse` | ✅ Full coverage |
| Sensor muster | Passed in parse request | ✅ Full coverage |
| Add separate PTU2 files | `POST /api/protocols/parse` | ✅ Can use same endpoint |
| Add separate TxAntDiag files | `POST /api/protocols/parse` | ✅ Can use same endpoint |
| Load limits files | `POST /api/limits/compute` | ✅ Full coverage |
| Clear Data button | `DELETE /api/protocols/clear` | ✅ Full coverage |
| Get parsed data count | `GET /api/stats/` | ✅ Full coverage |
| **Upload files from client** | `POST /api/protocols/upload` | ❌ **Not implemented** |

**Notes:**
- File upload from web client is the only missing feature
- Current API works with server-side file paths
- Can add multipart/form-data upload if needed for cloud deployment

---

### ✅ 2. System Diagrams Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| All configuration panels | `POST /api/system_diagrams/start` | ✅ Full Pydantic models |
| - Angle setup | `.plot_setup.targetAngle` | ✅ |
| - Sensor orientation | `.plot_setup.upsideDown` | ✅ |
| - Chirp selection | `.chirp_config` | ✅ |
| - Diagram config | `.diagram_config` | ✅ |
| - Image gen mode | `.plot_setup.imageDpi` | ✅ |
| - Plot scaling | `.plot_setup.xScale*` | ✅ |
| - Graph config | `.graph_config` | ✅ |
| - Slide layouts | `.two_graph_setup`, `.three_graph_setup`, etc. | ✅ |
| - Script vs window mode | Supported via config | ✅ |
| Start button | `POST /api/system_diagrams/start` | ✅ |
| Get defaults | `GET /api/system_diagrams/config/defaults` | ✅ |

**Status: 100% coverage**

---

### ✅ 3. TX Antenna Diagrams Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| All configuration panels | `POST /api/tx_diagrams/start` | ✅ Full Pydantic models |
| - Angle setup | `.plot_setup.targetAngle` | ✅ |
| - Sensor orientation | `.plot_setup.upsideDown` | ✅ |
| - Az/El selection | `.plot_setup.AzDiag/ElDiag` | ✅ |
| - Scaling | `.plot_setup.xScale*` | ✅ |
| - Orig/norm graphs | `.plot_setup.plotOrigGraphs/plotNormGraphs` | ✅ |
| - Graph config | `.graph_config` | ✅ |
| - Graphs per slide | `.plot_setup.graphsPerSlide` | ✅ |
| Start button | `POST /api/tx_diagrams/start` | ✅ |
| Get defaults | `GET /api/tx_diagrams/config/defaults` | ✅ |

**Status: 100% coverage**

---

### ✅ 4. Antenna Patterns Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| All configuration panels | `POST /api/antenna_patterns/start` | ✅ Full Pydantic models |
| - 8 tables config | `.ptu2_input_conf.tables` (array) | ✅ |
| - Pattern type | `.tables[i].patternType` | ✅ |
| - Rotation axis | `.tables[i].rotationAxis` | ✅ |
| - Gain calc method | `.tables[i].gainCalcMethod` | ✅ |
| - TX/RX antenna indices | `.tables[i].applTxAntInd/applRxAntInd` | ✅ |
| - Angle setup | `.ptu2_input_conf.targetAngle` | ✅ |
| - Sensor orientation | `.ptu2_input_conf.upsideDown` | ✅ |
| - Chirp selection | `.chirp_config` | ✅ |
| - Diagram type info | `.ptu2_input_conf.diagTypeInfo` | ✅ |
| - Output format | `.output_version` (0=JSON, 1/2=YAML) | ✅ |
| Start button | `POST /api/antenna_patterns/start` | ✅ |
| Get defaults | `GET /api/antenna_patterns/config/defaults` | ✅ |

**Status: 100% coverage**

---

### ✅ 5. Hüllkurven (Envelope Limits) Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| All configuration panels | `POST /api/huellkurven/start` | ✅ Full Pydantic models |
| - Az/El selection | `.data_conf.AzDiag/ElDiag` | ✅ |
| - Min/max sigma | `.data_conf.minSigma/maxSigma` | ✅ |
| - Pattern limits method | `.data_conf.patternLimitsMethod` | ✅ |
| - Chirp selection | `.chirp_config` | ✅ |
| - X-scale auto/manual | `.plot_setup.xScaleSizeAuto` | ✅ |
| Start button | `POST /api/huellkurven/start` | ✅ |
| Get defaults | `GET /api/huellkurven/config/defaults` | ✅ |

**Status: 100% coverage**

---

### ⚠️ 6. System Diagrams Interactive Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| Fill button (populate tables) | `POST /api/interactive/fill` | ✅ Returns protocol/param lists |
| Get current state | `GET /api/interactive/state` | ✅ |
| Clear | `DELETE /api/interactive/clear` | ✅ |
| **Toggle individual plots on/off** | N/A | ❌ **Not implemented** |
| **Real-time plot window** | N/A | ❌ **Not needed for web** |

**Notes:**
- The "fill" endpoint returns all protocols and parameters
- Web UI can implement toggle logic client-side
- Real-time Qt plot window doesn't translate to REST API (would need WebSocket/SSE)
- Missing feature: **POST /api/interactive/plot** to generate specific plot combinations
- **Recommendation**: Add endpoint to generate plots for selected protocol/parameter combinations

**Status: 75% coverage** (core data retrieval done, interactive plotting missing)

---

### ⚠️ 7. Statistics Tab

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| Compute statistics | `POST /api/limits/compute` | ✅ |
| View limits rows | `GET /api/limits/rows` | ✅ |
| View groups | `GET /api/limits/groups` | ✅ |
| Clear stats | `DELETE /api/limits/clear` | ✅ |
| Clear selected (plot reset) | GUI-only | ✅ N/A for API |
| **Navigate groups (forward/back)** | Client-side | ✅ Use /groups response |
| **Save group to YAML** | N/A | ❌ **Not implemented** |
| **Statistical series (histogram)** | N/A | ❌ **Not implemented** |
| **Export plot to PPTX** | N/A | ❌ **Not implemented** |
| Load config | Part of /compute | ✅ |

**Notes:**
- Group navigation is client-side (API returns full list)
- Missing features are visualization/persistence related
- **Recommendation**: Add these endpoints:
  - `POST /api/limits/groups/save` — save new group to YAML
  - `GET /api/limits/series/{limit_name}` — return histogram data
  - `POST /api/limits/export/pptx` — generate statistics PPTX

**Status: 70% coverage** (computation done, management features missing)

---

### ✅ 8. Downloads & File Management

| Qt GUI Feature | API Endpoint | Status |
|----------------|--------------|--------|
| List generated files | `GET /api/downloads/list/{type}` | ✅ |
| List recursively | `GET /api/downloads/list/{type}/recursive` | ✅ |
| Download file | `GET /api/downloads/download/{type}/{file}` | ✅ |
| Clear output directory | `DELETE /api/downloads/clear/{type}` | ✅ |

**Status: 100% coverage**

---

## Summary Table

| Tab | Coverage | Critical Gaps |
|-----|----------|---------------|
| Parse Protocols | 90% | File upload from client |
| System Diagrams | 100% | None |
| TX Diagrams | 100% | None |
| Antenna Patterns | 100% | None |
| Hüllkurven | 100% | None |
| Interactive | 75% | Interactive plot generation |
| Statistics | 70% | Group save, histogram, PPTX export |
| Downloads | 100% | None |

**Overall Coverage: 90%**

---

## Recommendations

### Priority 1: Add Missing Statistics Features

These are simple to implement and useful:

1. **POST /api/limits/groups/save**
   ```json
   {
     "group_name": "MyGroup",
     "limits_type": "burn_in",
     "limit_names": ["Temp_Sensor1", "Voltage_Rail1"],
     "match_type": "ExactMatch",
     "save_to_yaml": true
   }
   ```

2. **GET /api/limits/series/{limit_name}?limits_type=burn_in**
   - Returns histogram bins and values for statistical series visualization

3. **POST /api/limits/export/pptx**
   - Generate statistics plot PPTX (similar to group PPTX export in Qt GUI)

### Priority 2: Interactive Plot Generation (Optional)

4. **POST /api/interactive/plot**
   ```json
   {
     "protocols": ["2024-01-15_10-15-20_Tuner0_rf12345"],
     "parameters": ["level_AntType1_Diag0_RxCh0"],
     "output_format": "png"
   }
   ```
   - Returns base64-encoded plot or saves to downloads

### Priority 3: File Upload (For Cloud Deployment)

5. **POST /api/protocols/upload**
   - Multipart/form-data file upload
   - Only needed if API runs on different machine than protocol files

---

## Missing Qt GUI Features (Not Needed for API)

These are GUI-specific and don't need API equivalents:

- ❌ **Real-time plot windows** — Qt-specific, web UI will use canvas/images
- ❌ **Table cell color highlighting** — Frontend presentation logic
- ❌ **Progress bars** — Can use `/logs` endpoint for progress monitoring
- ❌ **File picker dialogs** — Web UI uses `<input type="file">` or path text boxes
- ❌ **Widget enable/disable logic** — Frontend state management

---

## Validation Checklist

### ✅ All Generation Workflows Work End-to-End
- [x] Parse protocols → System diagrams PPTX
- [x] Parse protocols → TX diagrams PPTX
- [x] Parse protocols → Antenna patterns YAML
- [x] Parse protocols → Hüllkurven DAT/PNG
- [x] Parse protocols → Compute limits statistics

### ✅ All Configuration Exposed
- [x] System diagrams: 10+ Pydantic models cover all panels
- [x] TX diagrams: All config exposed
- [x] Antenna patterns: 8-table setup fully modeled
- [x] Hüllkurven: All config exposed
- [x] Limits: File paths, extend options, groups

### ✅ All Clear/Reset Functions
- [x] Clear parsed data
- [x] Clear computed statistics
- [x] Clear interactive state
- [x] Clear output directories

### ✅ All Read/Download Functions
- [x] Get parsed data counts
- [x] Get limits rows
- [x] Get limits groups
- [x] Download generated files
- [x] List output directories

### ⚠️ Optional Enhancements
- [ ] Group save to YAML
- [ ] Statistical series histogram data
- [ ] Statistics PPTX export
- [ ] Interactive plot generation
- [ ] Client file upload

---

## Conclusion

The API has **90% coverage** of Qt GUI functionality with **100% coverage of all critical generation workflows**. The 10% gap consists of:

1. **Nice-to-have visualization features** (statistical series, PPTX export)
2. **GUI-specific features** that don't translate to REST APIs
3. **Optional enhancements** (file upload, interactive plotting)

**The API is production-ready for building a web UI** that replicates all core desktop app functionality. Remaining features can be added incrementally based on actual web UI requirements.
