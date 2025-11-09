# 📘 BookStack Export – Development Tasks & Requirements

This document describes all tasks and requirements for building a **HACS-compatible Home Assistant integration** that exports Home Assistant devices and entities to a connected **BookStack** instance.  
The goal is to generate a structured documentation of the smart home setup – organized by Areas, Rooms, and Devices – directly inside BookStack.

---

## 🧭 Project Overview

- **Name:** BookStack Export (Home Assistant Integration)
- **Goal:** Allow users to export all Home Assistant Devices and Entities into BookStack as structured pages and chapters.
- **Type:** Custom Integration (HACS-compatible)
- **Language:** Python 3.12+
- **Dependencies:** Uses Home Assistant’s internal registries and BookStack REST API.

---

## ✅ Functional Requirements

### 1. Core Features
- Retrieve all **Areas**, **Devices**, and **Entities** from Home Assistant.
- Group devices by their assigned **Area** (Room).
- Generate BookStack content in Markdown format for each device:
  - Device name, model, manufacturer
  - All entities belonging to the device
  - Entity attributes (power, state, etc.)
  - Last updated timestamps
- Automatically create or update BookStack:
  - **Book:** “Home Assistant Documentation”
  - **Chapters:** Represent Areas (e.g., “Living Room”, “Kitchen”)
  - **Pages:** Represent Devices inside each Area

### 2. Triggering the Export
- Provide a **service call**:
  ```yaml
  service: bookstack_export.export
  data:
    area_filter: "Living Room"  # optional
  ```
- Optionally allow export via:
  - **Automation trigger** (time-based or manual)
  - **UI button** in Home Assistant frontend

### 3. Configuration
- Integration configuration via **Config Flow (UI)**:
  - `BookStack URL`
  - `API Token`
  - Optional: `Target Book name`
- Validation of connection and credentials at setup.

### 4. Error Handling & Logging
- Handle BookStack API errors gracefully.
- Use Home Assistant’s `persistent_notification` for success/error messages.
- Log details to `home-assistant.log` with `LOGGER.debug()`.

### 5. Compatibility
- Support **HACS installation**
- Work with **Supervisor**, **Container**, and **Core** installations
- Tested against **Home Assistant 2024.12+**

---

## ⚙️ Technical Requirements

| Category | Requirement |
|-----------|--------------|
| **Language** | Python 3.12+ |
| **Home Assistant APIs** | `device_registry`, `entity_registry`, `area_registry` |
| **External API** | BookStack REST API (Token-based auth) |
| **Dependencies** | `requests` or `aiohttp` |
| **I/O** | HTTP(S) to BookStack endpoint |
| **Config storage** | Managed by `ConfigEntry` system |
| **Service schema** | Defined in `services.yaml` |
| **Tests** | Unit tests for BookStack client & exporter logic |

---

## 🧩 Integration File Structure

```
custom_components/bookstack_export/
├── __init__.py
├── manifest.json
├── config_flow.py
├── bookstack_api.py
├── exporter.py
├── services.yaml
├── const.py
└── strings.json
```

### File Descriptions

| File | Purpose |
|------|----------|
| `__init__.py` | Integration setup and service registration |
| `manifest.json` | Metadata for Home Assistant & HACS |
| `config_flow.py` | Handles configuration via the UI |
| `bookstack_api.py` | REST client for BookStack |
| `exporter.py` | Logic for formatting and exporting data |
| `services.yaml` | Defines service schema (`bookstack_export.export`) |
| `const.py` | Holds constants (domain name, defaults, etc.) |
| `strings.json` | UI localization strings |

---

## 🧠 Development Tasks

### Phase 1 – Project Setup
- [ ] Create project structure under `custom_components/bookstack_export/`
- [ ] Add `manifest.json` with minimal metadata
- [ ] Initialize GitHub repository and add `hacs.json`
- [ ] Create `.gitignore` and `requirements.txt`
- [ ] Set up virtual environment and basic Home Assistant dev container

### Phase 2 – Config Flow
- [ ] Implement UI-based setup using `config_flow.py`
- [ ] Test token and URL validation via BookStack API
- [ ] Store config in `ConfigEntry`

### Phase 3 – BookStack API Client
- [ ] Create `bookstack_api.py`
- [ ] Implement:
  - `create_book(name)`
  - `create_chapter(book_id, name)`
  - `create_or_update_page(chapter_id, name, markdown)`
- [ ] Implement authentication with BookStack token
- [ ] Add unit tests with mocked responses

### Phase 4 – Home Assistant Data Export
- [ ] Use `area_registry`, `device_registry`, and `entity_registry` to gather data
- [ ] Build Markdown representation for each device and its entities
- [ ] Implement `export_to_bookstack()` in `exporter.py`
- [ ] Handle missing Areas (e.g., devices without assigned area)

### Phase 5 – Service Definition
- [ ] Define service in `services.yaml`
- [ ] Register the service in `__init__.py`
- [ ] Implement optional `area_filter` parameter
- [ ] Add HA notifications after successful export

### Phase 6 – UI and Testing
- [ ] Add “Export to BookStack” button using `button` entity or dashboard card
- [ ] Add logging and persistent notifications
- [ ] Perform full integration test on a real HA instance
- [ ] Validate re-export overwrites existing BookStack pages

### Phase 7 – HACS Publication
- [ ] Add `hacs.json`
- [ ] Add `README.md` with installation instructions
- [ ] Add `info.md` for HACS store listing
- [ ] Tag version `v0.1.0` and publish GitHub release
- [ ] Submit to HACS default repository list (optional)

---

## 📦 Example Output (BookStack Page)

```markdown
# Shelly Plug S – TV Outlet

**Entity ID:** `switch.tv_power`  
**Manufacturer:** Shelly  
**Model:** Plug S  
**Firmware:** 2024.2.1  

**Attributes**
- Power: 22.3 W  
- Voltage: 231 V  
- Current: 0.1 A  

**Area:** Living Room  
**Last Updated:** 2025-11-09
```

---

## 🧪 Optional Enhancements (Future Tasks)

- [ ] Support for **BookStack page templating**
- [ ] Selective export by **domain** (e.g. only `sensor` or `switch`)
- [ ] Sync deletions (remove old pages no longer existing in HA)
- [ ] Export Home Assistant **dashboards** as embedded images
- [ ] Periodic scheduled export (daily/weekly)
- [ ] BookStack → Home Assistant import (reverse sync)

---

## 🧰 Development Tools

| Tool | Purpose |
|------|----------|
| **Visual Studio Code + Devcontainer** | Local HA integration development |
| **pytest + unittest.mock** | Automated testing |
| **Pre-commit hooks** | Linting & formatting |
| **Black + Flake8** | Python code style |
| **GitHub Actions** | CI/CD pipeline and release automation |

---

## 👥 Contributors & Ownership

- **Owner:** Christian Brosius  
- **Maintainers:** TBD  
- **Repository:** `github.com/cbrosius/homeassistant-bookstack-integration`

---

## 📄 License

MIT License (recommended for open-source HA integrations)

---

**Status:** Draft v0.1  
**Last updated:** 2025-11-09
