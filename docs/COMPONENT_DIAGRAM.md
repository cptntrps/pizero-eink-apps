# Pi Zero 2W Medicine Tracker - Component Interactions

**Version:** 2.0.0
**Last Updated:** November 8, 2025

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Core Component Relationships](#core-component-relationships)
3. [Display Component Hierarchy](#display-component-hierarchy)
4. [API Component Architecture](#api-component-architecture)
5. [Data Flow Between Components](#data-flow-between-components)
6. [Application Integration](#application-integration)
7. [Dependency Graph](#dependency-graph)
8. [Component Interaction Examples](#component-interaction-examples)

---

## Component Overview

The system is composed of several interconnected components organized in layers:

```mermaid
graph TB
    subgraph "Presentation Components"
        DISPLAY["Display System<br/>(E-ink Rendering)"]
        TOUCH["Touch Input<br/>(GT1151)"]
        WEB["Web Dashboard"]
    end

    subgraph "Application Components"
        APPS["Applications<br/>(medicine, pomodoro,<br/>weather, etc.)"]
    end

    subgraph "Service Components"
        API_SVC["API Service<br/>(Flask)"]
        DISPLAY_LIB["Display Library<br/>(Components)"]
        UTIL["Shared Utilities"]
    end

    subgraph "Data Components"
        DB["Database<br/>(SQLite)"]
        CONFIG["Configuration<br/>(JSON)"]
    end

    DISPLAY --> DISPLAY_LIB
    TOUCH --> DISPLAY_LIB
    WEB --> API_SVC

    APPS --> DISPLAY_LIB
    APPS --> TOUCH
    APPS --> UTIL
    APPS --> DB

    API_SVC --> UTIL
    API_SVC --> DB
    API_SVC --> CONFIG

    DISPLAY_LIB --> UTIL
```

---

## Core Component Relationships

### 1. Display Library Components

```mermaid
graph LR
    subgraph "Display Library Components"
        FONTS["fonts.py<br/>(Font Caching)"]
        CANVAS["canvas.py<br/>(Image Creation)"]
        SHAPES["shapes.py<br/>(Primitives)"]
        TEXT["text.py<br/>(Text Rendering)"]
        ICONS["icons.py<br/>(Icon Library)"]
        LAYOUTS["layouts.py<br/>(Page Layouts)"]
        COMPONENTS["components.py<br/>(UI Components)"]
        TOUCH["touch_handler.py<br/>(Input Handling)"]
    end

    CANVAS --> FONTS
    SHAPES --> CANVAS
    TEXT --> CANVAS
    TEXT --> FONTS
    ICONS --> CANVAS
    LAYOUTS --> CANVAS
    LAYOUTS --> SHAPES
    LAYOUTS --> TEXT
    COMPONENTS --> SHAPES
    COMPONENTS --> TEXT
    COMPONENTS --> ICONS
```

**Relationships**:
- **FONTS** (base): Loads and caches fonts for other components
- **CANVAS** (foundation): Creates PIL Image/ImageDraw objects
- **SHAPES** (uses Canvas): Draws lines, rectangles, circles
- **TEXT** (uses Canvas, Fonts): Renders text with sizing/wrapping
- **ICONS** (uses Canvas): Draws icons from library
- **LAYOUTS** (uses Shapes, Text): Positions content on page
- **COMPONENTS** (uses Shapes, Text, Icons): Complex UI elements
- **TOUCH** (independent): Handles GT1151 touch input asynchronously

---

### 2. Database Component Architecture

```mermaid
graph TB
    subgraph "Database Layer"
        MEDICINE_DB["MedicineDatabase<br/>(medicine_db.py)"]
        SCHEMA["Schema<br/>(schema.sql)"]
        CONN["Connections<br/>(Thread-local)"]
    end

    subgraph "Database Objects"
        MEDICINES["medicines<br/>table"]
        MED_DAYS["medicine_days<br/>table"]
        TRACKING["tracking<br/>table"]
        TIME_WIN["time_windows<br/>table"]
        METADATA["metadata<br/>table"]
    end

    subgraph "Query Interfaces"
        SYNC["Synchronous<br/>Queries"]
        TRANS["Transactions<br/>(context mgr)"]
    end

    MEDICINE_DB --> CONN
    MEDICINE_DB --> SCHEMA
    CONN --> MEDICINES
    CONN --> MED_DAYS
    CONN --> TRACKING
    CONN --> TIME_WIN
    CONN --> METADATA

    SYNC --> MEDICINE_DB
    TRANS --> MEDICINE_DB
```

**Relationships**:
- **MedicineDatabase**: Main interface, connection management
- **Connections**: Thread-local SQLite connections with WAL mode
- **Schema**: SQL table definitions, indexes, triggers, views
- **Medicines**: Core medicine definitions
- **Medicine_Days**: M2M relationship for scheduling
- **Tracking**: Adherence records
- **Time_Windows**: Predefined time slots
- **Metadata**: Schema versioning and timestamps

---

### 3. API Component Stack

```mermaid
graph TB
    subgraph "API Server"
        FLASK["Flask App<br/>(Factory Pattern)"]
        CONFIG["Configuration<br/>(development/prod)"]
        CORS["CORS<br/>(Cross-Origin)"]
    end

    subgraph "API v1 Blueprint"
        BP["Blueprint<br/>(api_v1_bp)"]
        ROUTES["Routes<br/>(endpoints)"]
        SERVICES["Services<br/>(business logic)"]
        SERIALIZERS["Serializers<br/>(JSON conversion)"]
    end

    subgraph "Route Modules"
        MED_ROUTES["medicines.py<br/>(CRUD)"]
        TRACK_ROUTES["tracking.py<br/>(Adherence)"]
        CONFIG_ROUTES["config.py<br/>(Settings)"]
    end

    FLASK --> CONFIG
    FLASK --> CORS
    FLASK --> BP
    BP --> ROUTES
    ROUTES --> SERVICES
    ROUTES --> SERIALIZERS
    ROUTES --> MED_ROUTES
    ROUTES --> TRACK_ROUTES
    ROUTES --> CONFIG_ROUTES
    SERVICES --> DB["Database"]
```

**Relationships**:
- **Flask**: WSGI server, request routing, error handling
- **Configuration**: Environment-specific settings
- **Blueprint**: Namespace for v1 API endpoints
- **Routes**: Request handlers, validation, response formatting
- **Services**: Business logic, database queries, calculations
- **Serializers**: JSON encoding/decoding, data transformation
- **Route Modules**: Specific resource implementations

---

## Display Component Hierarchy

### Component Dependency Tree

```
display/
├── fonts.py
│   └── Singleton Font Cache
│       ├── get_font(path, size)
│       ├── get_font_preset(name)
│       └── clear_font_cache()
│
├── canvas.py
│   └── Canvas Abstraction
│       ├── create_canvas(width=250, height=122)
│       └── Canvas class
│
├── shapes.py (depends: canvas)
│   ├── draw_line(draw, x0, y0, x1, y1, ...)
│   ├── draw_rectangle(draw, x, y, w, h, ...)
│   ├── draw_circle(draw, x, y, r, ...)
│   ├── draw_horizontal_line(...)
│   └── draw_vertical_line(...)
│
├── text.py (depends: canvas, fonts)
│   ├── draw_centered_text(draw, text, y, ...)
│   ├── draw_wrapped_text(draw, text, x, y, ...)
│   ├── truncate_text(text, max_width, ...)
│   └── get_text_size(text, font)
│
├── icons.py (depends: canvas)
│   ├── draw_pill_icon(draw, x, y, ...)
│   ├── draw_food_icon(draw, x, y, ...)
│   ├── draw_weather_icon(draw, x, y, ...)
│   ├── draw_compass_icon(draw, x, y, ...)
│   └── other icon functions
│
├── layouts.py (depends: shapes, text, canvas)
│   ├── HeaderLayout
│   │   └── draw(draw)
│   ├── FooterLayout
│   │   └── draw(draw)
│   ├── SplitLayout
│   │   └── draw(draw)
│   └── ListLayout
│       └── draw(draw)
│
├── components.py (depends: shapes, text, icons)
│   ├── StatusBar
│   │   └── draw(draw, status, ...)
│   ├── ProgressBar
│   │   └── draw(draw, current, total, ...)
│   ├── Button
│   │   └── draw(draw, text, x, y, ...)
│   └── Dialog
│       └── draw(draw, title, message, ...)
│
└── touch_handler.py (independent)
    ├── TouchHandler class
    ├── Event types (press, release, move)
    ├── Callback registration
    └── Thread management
```

### Component Usage Patterns

```mermaid
graph TB
    APP["Application"]

    APP -->|creates| CANVAS["Canvas"]
    APP -->|uses| LAYOUTS["Layouts"]
    APP -->|uses| COMPONENTS["Components"]
    APP -->|uses| ICONS["Icons"]
    APP -->|uses| FONTS["Fonts"]

    LAYOUTS -->|creates| CANVAS
    LAYOUTS -->|uses| SHAPES["Shapes"]
    LAYOUTS -->|uses| TEXT["Text"]

    COMPONENTS -->|uses| SHAPES
    COMPONENTS -->|uses| TEXT
    COMPONENTS -->|uses| ICONS

    TEXT -->|uses| FONTS
    TEXT -->|uses| CANVAS

    SHAPES -->|uses| CANVAS

    ICONS -->|uses| CANVAS

    APP -->|registers| TOUCH["TouchHandler"]
    TOUCH -->|calls back| APP
```

---

## API Component Architecture

### Request/Response Flow

```mermaid
graph LR
    CLIENT["HTTP Client"]
    FLASK["Flask<br/>Request Handler"]
    ROUTE["Route Handler<br/>(medicines.py)"]
    VALID["Validation<br/>(serializers)"]
    SERVICE["Service<br/>(business logic)"]
    DB["Database"]
    RESP["Response<br/>Serializer"]
    RESULT["JSON Response"]

    CLIENT -->|Request| FLASK
    FLASK -->|Route| ROUTE
    ROUTE -->|Validate| VALID
    VALID -->|Query| SERVICE
    SERVICE -->|SQL| DB
    DB -->|Result| SERVICE
    SERVICE -->|Format| RESP
    RESP -->|Response| RESULT
    RESULT -->|JSON| CLIENT
```

### API Route Organization

```
/api/v1/
├── medicines
│   ├── GET / (list all)
│   ├── POST / (create)
│   ├── GET /{id} (get one)
│   ├── PUT /{id} (update)
│   ├── DELETE /{id} (delete)
│   ├── GET /pending (pending medicines)
│   ├── GET /low-stock (low stock alerts)
│   └── POST /{id}/tracking (mark taken)
├── tracking
│   ├── GET / (list records)
│   ├── POST / (batch mark)
│   └── GET /today (today's stats)
└── config
    ├── GET / (all config)
    ├── PUT / (update all)
    ├── GET /{section} (get section)
    └── PATCH /{section} (update section)
```

---

## Data Flow Between Components

### Application → Display → Hardware

```mermaid
sequenceDiagram
    participant App as Application
    participant DLib as Display Library
    participant PIL as PIL/Pillow
    participant EPD as E-ink Display

    App->>DLib: create_canvas()
    DLib->>PIL: Image.new()
    PIL-->>DLib: img, draw
    DLib-->>App: canvas

    App->>DLib: draw_icon(draw, x, y)
    DLib->>PIL: draw.bitmap()
    PIL-->>DLib: updated

    App->>DLib: draw_text(draw, text)
    DLib->>PIL: draw.text()
    PIL-->>DLib: updated

    App->>EPD: displayPartial(buffer)
    EPD-->>App: displayed
```

### Application → Database → Storage

```mermaid
sequenceDiagram
    participant App as Application
    participant DAL as MedicineDatabase
    participant Conn as SQLite Conn
    participant Disk as Disk (medicine.db)

    App->>DAL: get_pending_medicines()
    DAL->>Conn: execute(sql)
    Conn->>Disk: Read medicines table
    Disk-->>Conn: rows
    Conn-->>DAL: sqlite3.Row objects
    DAL-->>App: List[Dict]

    App->>DAL: mark_medicine_taken()
    DAL->>Conn: execute(INSERT/UPDATE)
    Conn->>Disk: Write tracking table
    Disk-->>Conn: commit()
    Conn-->>DAL: success
    DAL-->>App: result dict
```

### API Server → Database → File

```mermaid
sequenceDiagram
    participant Client as Client
    participant API as API Handler
    participant Service as Service
    participant DAL as MedicineDatabase
    participant DB as SQLite
    participant Disk as Disk

    Client->>API: POST /api/v1/medicines
    API->>Service: create_medicine(data)
    Service->>DAL: insert_medicine(data)
    DAL->>DB: INSERT INTO medicines
    DB->>Disk: WAL write
    Disk-->>DB: ack
    DB-->>DAL: success
    DAL-->>Service: medicine dict
    Service->>API: result
    API->>Client: JSON 201 Created
```

---

## Application Integration

### Medicine App Integration

```mermaid
graph TB
    MAIN["medicine_app.py<br/>(main)"]
    INIT["Initialize<br/>Database & Display"]
    LOOP["Event Loop<br/>(1s cycle)"]
    RENDER["Render<br/>to Display"]
    INPUT["Handle Input<br/>(Touch)"]
    LOGIC["Update State<br/>(medicines, dates)"]

    MAIN -->|startup| INIT
    INIT -->|periodic| LOOP
    LOOP -->|per cycle| RENDER
    LOOP -->|per cycle| INPUT
    LOOP -->|per cycle| LOGIC

    RENDER -->|use| DISP_LIB["Display Library"]
    INPUT -->|use| TOUCH["TouchHandler"]
    LOGIC -->|use| DB["MedicineDatabase"]

    DISP_LIB -->|fonts, icons| COMP["Components"]
    DISP_LIB -->|layouts| LAYOUTS["Layouts"]

    TOUCH -->|events| LOGIC
    DB -->|medicines| LOGIC
```

### Pomodoro App Integration

```mermaid
graph TB
    POMO["pomodoro_app.py"]
    STATE["Timer State<br/>(work/break)"]
    DRAW["Draw UI<br/>(time, phase)"]
    TOUCH["Touch Events<br/>(start/pause)"]
    ANIM["Animation<br/>(tomato icon)"]

    POMO -->|manage| STATE
    POMO -->|periodic| DRAW
    POMO -->|poll| TOUCH
    POMO -->|periodic| ANIM

    DRAW -->|use| FONTS["Fonts"]
    DRAW -->|use| ICONS["Icons"]
    DRAW -->|use| SHAPES["Shapes"]
    ANIM -->|use| ICONS
    TOUCH -->|use| HANDLER["TouchHandler"]
```

---

## Dependency Graph

### Top-Level Dependencies

```
medicine_app.py
├── db.medicine_db (database operations)
├── shared.app_utils (utilities, config)
├── display (rendering)
│   ├── fonts
│   ├── canvas
│   ├── shapes
│   ├── text
│   ├── icons
│   ├── layouts
│   ├── components
│   └── touch_handler
├── TP_lib (hardware drivers)
└── PIL (image manipulation)

api/__init__.py
├── flask (web framework)
├── flask_cors
├── api.config (configuration)
├── api.v1 (blueprint)
│   ├── routes.medicines
│   ├── routes.tracking
│   ├── routes.config
│   ├── services.* (business logic)
│   └── serializers.* (JSON)
├── db.medicine_db
└── shared.* (utilities)

pomodoro_app.py
├── shared.app_utils
├── display.*
├── TP_lib
└── PIL

web_config.py
├── flask
├── json
└── os/sys
```

### Circular Dependency Analysis

**Result**: No circular dependencies detected

**Key principle**: Unidirectional dependency flow
- Applications → Libraries
- API → Database
- Display → Fonts (caching)
- No reverse dependencies

---

## Component Interaction Examples

### Example 1: Display a Medicine Reminder

```mermaid
sequenceDiagram
    participant DB as Database
    participant App as medicine_app.py
    participant Handler as TouchHandler
    participant DLib as Display Library
    participant EPD as E-ink Display

    App->>DB: get_pending_medicines()
    DB-->>App: [Aspirin, Vitamin D]

    App->>DLib: create_canvas()
    DLib-->>App: (img, draw)

    App->>DLib: draw_pill_icon(draw, x, y)
    App->>DLib: draw_text(draw, "Take Aspirin")
    App->>DLib: draw_centered_text(draw, "500mg", y=80)

    App->>EPD: displayPartial(buffer)
    EPD-->>App: displayed

    Handler-->>App: on_press(x, y)
    App->>App: identify_medicine(x, y)
    App->>DB: mark_medicine_taken(med_id)
    DB-->>App: success

    App->>DLib: draw_checkmark()
    App->>EPD: displayPartial(buffer)
    EPD-->>App: confirmed
```

### Example 2: Update Medicine via API

```mermaid
sequenceDiagram
    participant Client as Web Client
    participant API as Flask API
    participant Serializer as Input Serializer
    participant Service as Medicine Service
    participant DB as MedicineDatabase
    participant Disk as SQLite Disk

    Client->>API: PUT /api/v1/medicines/med_001
    API->>Serializer: validate(request.json)
    Serializer-->>API: validated_data

    API->>Service: update_medicine(med_id, validated_data)
    Service->>DB: update_medicine(med_id, **data)

    DB->>Disk: UPDATE medicines SET ...
    Disk-->>DB: trigger: update timestamp
    Disk-->>DB: committed

    DB-->>Service: updated_medicine_dict
    Service-->>API: result

    API->>API: serialize_response(result)
    API-->>Client: JSON 200 OK
```

### Example 3: Get Daily Adherence Stats

```mermaid
sequenceDiagram
    participant CLI as CLI/API Client
    participant Service as API Service
    participant DB as MedicineDatabase
    participant Disk as SQLite Disk

    CLI->>Service: get_today_stats()
    Service->>DB: execute view query

    DB->>Disk: SELECT FROM v_today_stats
    Disk-->>DB: (date, total, taken, percentage)

    DB->>DB: format_response(row)
    DB-->>Service: stats_dict

    Service-->>CLI: {date, total_medicines: 3, medicines_taken: 2, adherence: 66.7}
```

---

## Component Communication Protocols

### 1. Synchronous Request/Response

**Used by**: Applications ↔ Database, API ↔ Database

```python
# Application requests data
medicines = db.get_pending_medicines()
# Blocks until response received
```

### 2. Asynchronous Event Handling

**Used by**: TouchHandler → Application callbacks

```python
def on_touch(x, y):
    # Non-blocking callback
    process_touch_event(x, y)

handler.register_press_callback(on_touch)
# Callback invoked asynchronously in separate thread
```

### 3. Configuration-based

**Used by**: Applications ↔ ConfigLoader

```python
config = ConfigLoader()
update_interval = config.get_section('medicine').get('update_interval', 60)
# Reads once on startup, no real-time updates
```

### 4. REST API

**Used by**: Web Clients ↔ Flask API

```
GET /api/v1/medicines
Content-Type: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{
    "success": true,
    "data": [...],
    "meta": {"timestamp": "2025-11-08T..."}
}
```

---

## Component Testing

### Isolated Component Testing

```mermaid
graph TB
    FONTS_TEST["fonts_test.py<br/>(Font loading)"]
    CANVAS_TEST["canvas_test.py<br/>(Image creation)"]
    TOUCH_TEST["touch_test.py<br/>(Input handling)"]
    DB_TEST["database_test.py<br/>(CRUD ops)"]
    API_TEST["api_test.py<br/>(Endpoints)"]

    FONTS_TEST -.->|no deps| FONTS
    CANVAS_TEST -.->|mock only| FONTS
    TOUCH_TEST -.->|mock only| TP_LIB
    DB_TEST -.->|mock| DISK
    API_TEST -.->|mock| DB

    FONTS["Fonts"]
    TP_LIB["TP_lib"]
    DISK["Disk"]
    DB["Database"]
```

### Integration Testing

```mermaid
graph TB
    DISPLAY_TEST["Display integration<br/>(fonts+canvas+shapes)"]
    MEDICINE_APP_TEST["Medicine app<br/>(app+db+display)"]
    API_TEST["API integration<br/>(routes+db)"]

    DISPLAY_TEST -->|tests| FONTS
    DISPLAY_TEST -->|tests| CANVAS
    DISPLAY_TEST -->|tests| SHAPES

    MEDICINE_APP_TEST -->|tests| APP
    MEDICINE_APP_TEST -->|uses test| DB

    API_TEST -->|tests| API
    API_TEST -->|uses test| DB
```

---

## Performance Characteristics

### Component Latency

| Component | Operation | Latency | Notes |
|-----------|-----------|---------|-------|
| Fonts | Load/cache | 10-50ms | Disk I/O, first load only |
| Fonts | Render text | 1-5ms | In-memory, rapid |
| Canvas | Create | <1ms | Memory allocation |
| Icons | Draw | <1ms | Pre-computed bitmaps |
| TouchHandler | Detect event | 10-100ms | Polling interval |
| Database | Simple query | 1-10ms | Cached, indexed |
| Database | Complex query | 10-100ms | Join, group by |
| API | Request/response | 50-200ms | I/O + processing |

### Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| Canvas (250x122) | ~30KB | PIL Image + ImageDraw |
| Font cache (10 fonts) | ~5MB | Loaded in RAM |
| TouchHandler | <1MB | Event queue + callbacks |
| MedicineDatabase | <5MB | Connection + statement cache |
| Flask app | ~20MB | With all routes loaded |

---

## Summary

The component architecture achieves:

1. **Modularity**: Each component has clear responsibilities
2. **Reusability**: Display library used by multiple apps
3. **Testability**: Components can be tested in isolation
4. **Maintainability**: Clear dependencies and communication paths
5. **Scalability**: New components easily added without breaking changes
6. **Performance**: Optimized data flows and caching strategies

---

**See Also**:
- `/docs/ARCHITECTURE.md` - System-level architecture
- `/docs/DATABASE_SCHEMA.md` - Database design
- `/docs/DATA_FLOW.md` - Data movement through system
- Source code in `/display/`, `/api/`, `/db/`, `/shared/`
