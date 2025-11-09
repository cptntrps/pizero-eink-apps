# Pi Zero 2W Medicine Tracker - Data Flow Diagrams

**Version:** 2.0.0
**Last Updated:** November 8, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [High-Level System Data Flow](#high-level-system-data-flow)
3. [Medicine Tracking Flow](#medicine-tracking-flow)
4. [API Data Flow](#api-data-flow)
5. [Configuration Management Flow](#configuration-management-flow)
6. [Touch Input Flow](#touch-input-flow)
7. [Display Rendering Flow](#display-rendering-flow)
8. [Database Operations Flow](#database-operations-flow)
9. [Backup and Recovery Flow](#backup-and-recovery-flow)
10. [Error Handling Flow](#error-handling-flow)

---

## Overview

Data flows through the system via several distinct paths:

1. **User → Display** (touch input)
2. **Display → User** (rendered output)
3. **App ↔ Database** (persistence)
4. **Web Client ↔ API** (remote management)
5. **Configuration** (settings management)

Each path has specific data formats, transformations, and error handling.

---

## High-Level System Data Flow

### Complete System Flow

```mermaid
graph TB
    subgraph "Input Sources"
        USER["👤 User Input<br/>(touch)"]
        CONFIG_FILE["⚙ Configuration<br/>(JSON)"]
        WEB_CLIENT["🌐 Web Client<br/>(HTTP)"]
    end

    subgraph "Processing"
        TOUCH_H["TouchHandler<br/>(event detection)"]
        CONFIG_L["ConfigLoader<br/>(JSON parsing)"]
        API["Flask API<br/>(request routing)"]
        APPS["Applications<br/>(business logic)"]
    end

    subgraph "Storage"
        MEDICINE_DB["SQLite Database<br/>(medicine.db)"]
        CONFIG_JSON["Config File<br/>(config.json)"]
    end

    subgraph "Output"
        DISPLAY["E-ink Display<br/>(rendered output)"]
    end

    USER -->|touch event| TOUCH_H
    TOUCH_H -->|callback| APPS

    CONFIG_FILE -->|load| CONFIG_L
    CONFIG_L -->|app config| APPS

    WEB_CLIENT -->|HTTP request| API
    API -->|process| APPS

    APPS -->|read/write| MEDICINE_DB
    APPS -->|render| DISPLAY

    API -->|read/write| MEDICINE_DB
    API -->|read/write| CONFIG_JSON

    MEDICINE_DB -->|query results| APPS
    MEDICINE_DB -->|query results| API

    CONFIG_JSON -->|read| CONFIG_L
```

---

## Medicine Tracking Flow

### Primary Use Case: Mark Medicine as Taken

```mermaid
sequenceDiagram
    participant User
    participant Display as E-ink Display
    participant App as medicine_app.py
    participant Handler as TouchHandler
    participant DB as MedicineDatabase
    participant Disk as Disk (medicine.db)

    User->>Display: View medicine reminder
    Display->>App: Rendered display

    User->>Display: Touch pill area
    Display->>Handler: Touch coordinates (x, y)
    Handler->>App: on_touch_press(x, y)

    App->>App: identify_medicine(x, y)
    Note over App: Determine which medicine<br/>user touched

    App->>DB: mark_medicine_taken(med_id)
    DB->>Disk: INSERT INTO tracking<br/>(medicine_id, date, time_window, taken)
    Disk->>DB: success

    DB->>App: {success: true, pills_remaining: 44}

    App->>App: update_state()
    App->>Display: Draw checkmark icon
    Display->>User: Confirmation displayed

    Note over DB: Database now contains:<br/>- Updated pills_remaining<br/>- New tracking record<br/>- Updated metadata timestamp
```

### Get Pending Medicines Flow

```mermaid
graph TB
    subgraph "Startup"
        START["Application<br/>starts"]
        INIT_DB["Initialize<br/>Database"]
        LOAD_CONFIG["Load<br/>config.json"]
    end

    subgraph "Medicine Retrieval"
        GET_PEND["get_pending_medicines()"]
        GET_TODAY["Get today's<br/>medicines"]
        CHECK_TIME["Check time<br/>windows"]
        FILTER["Filter active<br/>medicines"]
    end

    subgraph "Database Query"
        QUERY["SELECT medicines<br/>WHERE time window<br/>matches current"]
        INDEX["Use<br/>idx_medicines_active<br/>idx_medicines_time_window"]
        RESULT["List of pending<br/>medicines"]
    end

    subgraph "Display"
        RENDER["Render<br/>medicines on<br/>display"]
        SHOW["Show to<br/>user"]
    end

    START --> INIT_DB
    INIT_DB --> LOAD_CONFIG
    LOAD_CONFIG --> GET_PEND

    GET_PEND --> GET_TODAY
    GET_TODAY --> CHECK_TIME
    CHECK_TIME --> FILTER

    FILTER --> QUERY
    QUERY --> INDEX
    INDEX --> RESULT

    RESULT --> RENDER
    RENDER --> SHOW
```

### Daily Statistics Flow

```mermaid
graph LR
    subgraph "Data Collection"
        TRACK["Tracking<br/>records"]
        DATE["Today's<br/>date"]
    end

    subgraph "Query Processing"
        VIEW["v_today_stats<br/>(SQL view)"]
        COUNT["COUNT taken<br/>medicines"]
        CALC["Calculate<br/>adherence %"]
    end

    subgraph "Result"
        STATS["Daily Stats<br/>(JSON)"]
        DISPLAY["Display<br/>on screen"]
    end

    TRACK --> VIEW
    DATE --> VIEW
    VIEW --> COUNT
    COUNT --> CALC
    CALC --> STATS
    STATS --> DISPLAY
```

---

## API Data Flow

### Medicines CRUD Operations

#### Create Medicine

```mermaid
sequenceDiagram
    participant Client as Web Client
    participant API as Flask API
    participant Serializer as Request Validation
    participant Service as Medicine Service
    participant DB as MedicineDatabase
    participant Disk as SQLite

    Client->>API: POST /api/v1/medicines
    Note over API: Content-Type: application/json

    activate API
    API->>Serializer: validate(request.json)

    activate Serializer
    Serializer->>Serializer: Check name, dosage<br/>Check time_window<br/>Validate days list

    alt Validation fails
        Serializer->>API: {errors: {...}}
        API->>Client: 400 Bad Request
    else Validation succeeds
        Serializer->>API: validated_data
    end
    deactivate Serializer

    API->>Service: create_medicine(validated_data)

    activate Service
    Service->>Service: Generate UUID<br/>Set default values<br/>Prepare SQL
    Service->>DB: insert_medicine(data)
    deactivate Service

    activate DB
    DB->>Disk: BEGIN TRANSACTION
    DB->>Disk: INSERT INTO medicines
    DB->>Disk: INSERT INTO medicine_days (for each day)
    DB->>Disk: UPDATE metadata
    Disk->>DB: COMMIT
    DB->>DB: Format response
    DB->>API: medicine_dict
    deactivate DB

    deactivate API

    API->>Client: 201 Created<br/>{medicine_id, name, ...}
```

#### Read Medicine (List and Get)

```mermaid
graph TB
    subgraph "List All Medicines"
        REQ["GET /api/v1/medicines"]
        SERVICE["get_all_medicines()"]
        QUERY["SELECT m.*, days<br/>FROM v_medicines_with_days"]
        INDEX["Use<br/>idx_medicines_active"]
        ROWS["Fetch all rows"]
        FORMAT["Format as JSON"]
        RESP["Return list"]
    end

    subgraph "Get Single Medicine"
        REQ2["GET /api/v1/medicines/{id}"]
        SERVICE2["get_medicine_by_id(id)"]
        QUERY2["SELECT * WHERE id = ?"]
        SINGLE["Fetch single row"]
        FORMAT2["Format as JSON"]
        RESP2["Return medicine"]
    end

    REQ --> SERVICE
    SERVICE --> QUERY
    QUERY --> INDEX
    INDEX --> ROWS
    ROWS --> FORMAT
    FORMAT --> RESP

    REQ2 --> SERVICE2
    SERVICE2 --> QUERY2
    QUERY2 --> SINGLE
    SINGLE --> FORMAT2
    FORMAT2 --> RESP2
```

#### Update Medicine

```mermaid
graph TB
    subgraph "Update Steps"
        REQ["PUT /api/v1/medicines/{id}"]
        VALIDATE["Validate input<br/>data"]
        LOCK["Get medicine<br/>for update"]
        CHECK["Verify exists"]

        UPDATE_MED["UPDATE medicines<br/>table"]
        UPDATE_DAYS["DELETE old days<br/>INSERT new days"]
        TRIGGER["triggers fire:<br/>update timestamp<br/>update metadata"]

        FORMAT["Format response"]
        RESP["Return updated"]
    end

    REQ --> VALIDATE
    VALIDATE --> LOCK
    LOCK --> CHECK
    CHECK --> UPDATE_MED
    UPDATE_MED --> UPDATE_DAYS
    UPDATE_DAYS --> TRIGGER
    TRIGGER --> FORMAT
    FORMAT --> RESP
```

#### Delete Medicine

```mermaid
graph TB
    subgraph "Cascade Delete"
        REQ["DELETE /api/v1/medicines/{id}"]
        VALIDATE["Validate id"]
        BACKUP["Backup data<br/>(optional)"]

        DELETE_TRACK["DELETE tracking<br/>records<br/>(via FK cascade)"]
        DELETE_DAYS["DELETE medicine_days<br/>records<br/>(via FK cascade)"]
        DELETE_MED["DELETE medicine"]
        TRIGGER["Trigger updates<br/>metadata"]

        RESP["Return success"]
    end

    REQ --> VALIDATE
    VALIDATE --> BACKUP
    BACKUP --> DELETE_TRACK
    DELETE_TRACK --> DELETE_DAYS
    DELETE_DAYS --> DELETE_MED
    DELETE_MED --> TRIGGER
    TRIGGER --> RESP
```

### Tracking Operations

#### Mark Medicines Taken

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant DB
    participant Disk

    Client->>API: POST /api/v1/tracking<br/>[med_ids]

    loop For each medicine
        API->>Service: mark_medicine_taken(med_id)
        Service->>DB: Check exists + active
        DB-->>Service: medicine data

        Service->>DB: Insert/update tracking
        DB->>Disk: INSERT tracking<br/>(taken=1)
        Disk-->>DB: success

        DB->>DB: Check pills_remaining<br/>vs threshold
        DB-->>Service: {success, pills_remaining}
        Service-->>API: result
    end

    API->>Client: 200 OK<br/>{results: [...]}
```

#### Get Daily Statistics

```mermaid
graph TB
    subgraph "Statistics Query"
        REQ["GET /api/v1/tracking/today"]
        SERVICE["get_today_stats()"]
        VIEW["Query v_today_stats"]

        COUNT_TOTAL["COUNT distinct<br/>medicines<br/>for today"]
        COUNT_TAKEN["COUNT medicines<br/>with taken=1"]

        CALC["Calculate<br/>percentage"]
        FORMAT["Format response"]
    end

    REQ --> SERVICE
    SERVICE --> VIEW
    VIEW --> COUNT_TOTAL
    VIEW --> COUNT_TAKEN
    COUNT_TAKEN --> CALC
    COUNT_TOTAL --> CALC
    CALC --> FORMAT
```

---

## Configuration Management Flow

### Configuration Loading

```mermaid
graph TB
    subgraph "Startup"
        START["App starts"]
        LOAD["ConfigLoader()"]
        READ["Read config.json"]
        PARSE["JSON parse"]
        CACHE["In-memory cache"]
    end

    subgraph "Usage"
        GET["get_section(name)"]
        RETURN["Return section dict"]
        DEFAULT["Apply defaults"]
    end

    subgraph "Updates"
        API_UPD["API: PATCH /config"]
        VALIDATE["Validate input"]
        WRITE["Write to disk"]
        NOTIFY["Notify app"]
    end

    START --> LOAD
    LOAD --> READ
    READ --> PARSE
    PARSE --> CACHE

    GET --> CACHE
    CACHE --> RETURN
    RETURN --> DEFAULT

    API_UPD --> VALIDATE
    VALIDATE --> WRITE
    WRITE --> NOTIFY
```

### Configuration File Format

```json
{
    "medicine": {
        "update_interval": 60,
        "reminder_window": 30,
        "display_refresh": "partial",
        "low_stock_threshold": 10
    },
    "pomodoro": {
        "work_duration": 25,
        "break_duration": 5
    },
    "display": {
        "width": 250,
        "height": 122,
        "font_size": 12
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": false
    }
}
```

---

## Touch Input Flow

### Touch Event Detection and Handling

```mermaid
sequenceDiagram
    participant User
    participant GT1151 as GT1151 Touch<br/>Controller
    participant Handler as TouchHandler
    participant App as medicine_app
    participant Callback as Touch Callback

    User->>GT1151: Tap display
    Note over GT1151: Register capacitive touch

    GT1151->>GT1151: Store event in<br/>controller buffer

    Handler->>Handler: Poll GT1151<br/>(every 100ms)
    GT1151->>Handler: Event data<br/>(x, y, pressure)

    Handler->>Handler: Decode event<br/>type (press/release)

    alt Press detected
        Handler->>Callback: on_press(x, y)
    else Release detected
        Handler->>Callback: on_release(x, y)
    else Move detected
        Handler->>Callback: on_move(x, y)
    end

    Callback->>App: Registered callback

    activate App
    App->>App: Identify touched<br/>medicine
    App->>App: Update state
    deactivate App
```

### Touch Coordinate Mapping

```mermaid
graph TB
    subgraph "Raw Event"
        RAW["Raw coords<br/>from GT1151<br/>(0-319, 0-479)"]
    end

    subgraph "Mapping"
        ROTATE["Rotate/flip<br/>to match display<br/>orientation"]
        SCALE["Scale to<br/>display resolution<br/>(250x122)"]
        BOUND["Clamp to<br/>bounds"]
    end

    subgraph "Processing"
        IDENTIFY["Identify<br/>UI element"]
        HIT_TEST["Collision detection"]
        CALLBACK["Invoke callback"]
    end

    RAW --> ROTATE
    ROTATE --> SCALE
    SCALE --> BOUND
    BOUND --> IDENTIFY
    IDENTIFY --> HIT_TEST
    HIT_TEST --> CALLBACK
```

---

## Display Rendering Flow

### Rendering Pipeline

```mermaid
graph TB
    subgraph "Data Preparation"
        APP["Application<br/>state"]
        FETCH["Fetch display<br/>data from DB"]
        FORMAT["Format for<br/>rendering"]
    end

    subgraph "Rendering"
        CANVAS["Create canvas<br/>(PIL Image)"]
        DRAW["Draw components<br/>- fonts<br/>- shapes<br/>- icons<br/>- text"]
        BUFFER["Generate buffer<br/>(image→bytes)"]
    end

    subgraph "Display Update"
        REFRESH["Refresh type<br/>(full/partial)"]
        TRANSFER["Transfer buffer<br/>to EPD"]
        UPDATE["E-ink update"]
    end

    APP --> FETCH
    FETCH --> FORMAT
    FORMAT --> CANVAS
    CANVAS --> DRAW
    DRAW --> BUFFER
    BUFFER --> REFRESH
    REFRESH --> TRANSFER
    TRANSFER --> UPDATE
```

### Component Rendering Order

```mermaid
graph TB
    subgraph "Layout"
        CANVAS["Clear canvas"]
        HEADER["Draw header<br/>(title, time)"]
        BODY["Draw body<br/>(main content)"]
        FOOTER["Draw footer<br/>(controls)"]
    end

    subgraph "Body Content"
        ICONS_DRAW["Draw icons<br/>(pills, food)"]
        TEXT_DRAW["Draw text<br/>(medicine names)"]
        LINES["Draw dividers"]
    end

    subgraph "Buffer"
        CONVERT["PIL Image →<br/>bytes buffer"]
        EPD_UPD["EPD display<br/>update"]
    end

    CANVAS --> HEADER
    HEADER --> BODY
    BODY --> ICONS_DRAW
    BODY --> TEXT_DRAW
    ICONS_DRAW --> LINES
    TEXT_DRAW --> LINES
    LINES --> CONVERT
    CONVERT --> EPD_UPD
```

### Display Refresh Types

```mermaid
graph LR
    subgraph "Full Refresh"
        FULL["Redraw entire<br/>display<br/>(slow: 2-3s)"]
        USE_FULL["Use when:<br/>- Major changes<br/>- Startup<br/>- Clear ghosting"]
    end

    subgraph "Partial Refresh"
        PARTIAL["Update changed<br/>regions only<br/>(fast: 100-500ms)"]
        USE_PARTIAL["Use when:<br/>- Minor updates<br/>- Real-time<br/>- Lower power"]
    end

    FULL --> USE_FULL
    PARTIAL --> USE_PARTIAL
```

---

## Database Operations Flow

### Query Execution Flow

```mermaid
graph TB
    subgraph "Preparation"
        APP["Application<br/>calls method"]
        METHOD["e.g., get_pending<br/>_medicines()"]
        SQL["Prepare SQL<br/>query"]
    end

    subgraph "Execution"
        CONN["Get thread-local<br/>connection"]
        EXEC["Execute SQL"]
        FETCH["Fetch results"]
        FORMAT["Format rows as<br/>Dict/List"]
    end

    subgraph "Return"
        RESULT["Return to<br/>application"]
    end

    APP --> METHOD
    METHOD --> SQL
    SQL --> CONN
    CONN --> EXEC
    EXEC --> FETCH
    FETCH --> FORMAT
    FORMAT --> RESULT
```

### Transaction Flow

```mermaid
sequenceDiagram
    participant App
    participant DB as MedicineDatabase
    participant Conn as SQLite Connection
    participant Disk

    App->>DB: with db.transaction() as conn:

    activate DB
    DB->>Conn: Get connection
    DB->>Conn: BEGIN TRANSACTION
    activate Conn

    App->>Conn: Execute SQL statements

    alt Errors occur
        Conn->>Conn: ROLLBACK
        DB->>App: Raise exception
        Note over DB: All changes undone
    else Success
        Conn->>Disk: COMMIT
        Disk->>Conn: ack
        deactivate Conn
    end

    deactivate DB

    Note over DB: Context manager<br/>ensures cleanup
```

### Index Usage Flow

```mermaid
graph TB
    subgraph "Query Analysis"
        QUERY["SQL query"]
        ANALYZE["Query planner"]
        CANDIDATES["Find candidate<br/>indexes"]
    end

    subgraph "Index Selection"
        COST["Estimate cost<br/>with/without"]
        SELECT["Select best<br/>index"]
    end

    subgraph "Execution"
        SEEK["Use index<br/>to seek rows"]
        FETCH_ROWS["Fetch matching<br/>rows"]
        RESULT["Return result"]
    end

    QUERY --> ANALYZE
    ANALYZE --> CANDIDATES
    CANDIDATES --> COST
    COST --> SELECT
    SELECT --> SEEK
    SEEK --> FETCH_ROWS
    FETCH_ROWS --> RESULT
```

---

## Backup and Recovery Flow

### Backup Creation

```mermaid
sequenceDiagram
    participant App
    participant Backup as backup.py
    participant Source as medicine.db
    participant Dest as backup/migration_*.db
    participant Metadata as metadata

    App->>Backup: create_backup()
    activate Backup

    Backup->>Source: Open for reading
    Backup->>Dest: Copy file
    Source-->>Dest: Complete copy

    Backup->>Metadata: Record timestamp
    Metadata->>Backup: backup_path
    Backup->>App: backup_path
    deactivate Backup
```

### Data Recovery

```mermaid
graph TB
    subgraph "Detect Corruption"
        CHECK["PRAGMA integrity_check"]
        ERROR["Error detected"]
    end

    subgraph "Recovery Process"
        FIND["Find latest<br/>backup"]
        VERIFY["Verify backup<br/>integrity"]
        RESTORE["Restore from<br/>backup"]
        VERIFY2["Verify restored<br/>database"]
    end

    subgraph "Result"
        SUCCESS["Database recovered"]
        LOG["Log recovery event"]
    end

    CHECK --> ERROR
    ERROR --> FIND
    FIND --> VERIFY
    VERIFY --> RESTORE
    RESTORE --> VERIFY2
    VERIFY2 --> SUCCESS
    SUCCESS --> LOG
```

### JSON to SQLite Migration

```mermaid
sequenceDiagram
    participant User
    participant Migration as migrate_to_sqlite.py
    participant JSON as medicine_data.json
    participant DB as medicine.db

    User->>Migration: Run migration script

    Migration->>JSON: Read JSON file
    JSON-->>Migration: medicines[], tracking{}

    loop For each medicine
        Migration->>Migration: Parse data
        Migration->>Migration: Generate UUID
        Migration->>DB: INSERT medicine
        Migration->>DB: INSERT medicine_days
    end

    loop For each tracking record
        Migration->>DB: INSERT tracking
    end

    Migration->>DB: Verify integrity
    DB-->>Migration: OK

    Migration->>User: Migration complete
```

---

## Error Handling Flow

### Application Error Handling

```mermaid
graph TB
    subgraph "Error Detection"
        TRY["try block"]
        EXCEPT["Exception<br/>raised"]
    end

    subgraph "Error Classification"
        TYPE["Determine type<br/>- Database error<br/>- Display error<br/>- Input error"]
        LOG["Log error<br/>with context"]
    end

    subgraph "Recovery"
        USER_ERR["User error<br/>(validation fail)"]
        SYSTEM_ERR["System error<br/>(hardware issue)"]

        USER_ERR --> NOTIFY["Notify user<br/>on display"]
        SYSTEM_ERR --> RETRY["Retry logic"]
        RETRY --> FALLBACK["Fallback behavior"]
    end

    subgraph "Cleanup"
        CLEANUP["Release resources<br/>- Close DB<br/>- Clean display"]
        LOG_FINAL["Log resolution"]
    end

    TRY --> EXCEPT
    EXCEPT --> TYPE
    TYPE --> LOG
    LOG --> USER_ERR
    LOG --> SYSTEM_ERR
    USER_ERR --> NOTIFY
    SYSTEM_ERR --> FALLBACK
    NOTIFY --> CLEANUP
    FALLBACK --> CLEANUP
    CLEANUP --> LOG_FINAL
```

### API Error Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Handler
    participant Serializer
    participant Service
    participant DB

    Client->>API: Request with bad data

    API->>Handler: Route to handler
    Handler->>Serializer: Validate data

    alt Validation fails
        Serializer-->>Handler: ValidationError
        Handler->>API: error dict
        API-->>Client: 400 Bad Request<br/>{errors: [...]}
    end

    Handler->>Service: Valid request
    Service->>DB: Query database

    alt Database error
        DB-->>Service: DatabaseError
        Service-->>Handler: error dict
        Handler->>API: error dict
        API-->>Client: 500 Internal Error<br/>{error: "..."}
        Note over API: Logged for debugging
    end

    DB-->>Service: Results
    Service-->>Handler: Response data
    Handler->>API: Response dict
    API-->>Client: 200 OK<br/>{data: [...]}
```

---

## Data Transformation Pipeline

### Input Validation and Transformation

```mermaid
graph TB
    subgraph "Raw Input"
        JSON_STR["JSON string<br/>from client"]
    end

    subgraph "Parsing"
        PARSE["Parse JSON<br/>to dict"]
        TYPE_CHECK["Type checking"]
    end

    subgraph "Validation"
        REQUIRED["Check required<br/>fields"]
        CONSTRAINTS["Check constraints<br/>- range<br/>- enum<br/>- format"]
        CUSTOM["Custom validation<br/>- unique id<br/>- references"]
    end

    subgraph "Transformation"
        NORMALIZE["Normalize<br/>- trim whitespace<br/>- lowercase"]
        CONVERT["Convert types<br/>- str→int<br/>- str→date"]
    end

    subgraph "Output"
        VALIDATED["Validated<br/>data dict"]
    end

    JSON_STR --> PARSE
    PARSE --> TYPE_CHECK
    TYPE_CHECK --> REQUIRED
    REQUIRED --> CONSTRAINTS
    CONSTRAINTS --> CUSTOM
    CUSTOM --> NORMALIZE
    NORMALIZE --> CONVERT
    CONVERT --> VALIDATED
```

### Output Serialization

```mermaid
graph TB
    subgraph "Database Objects"
        ROW["sqlite3.Row<br/>objects"]
    end

    subgraph "Conversion"
        TO_DICT["Convert to<br/>dict"]
        TYPE_FIX["Fix types<br/>- int→bool<br/>- str→date"]
    end

    subgraph "Enrichment"
        ADD_META["Add metadata<br/>- timestamps<br/>- computed fields"]
    end

    subgraph "Serialization"
        TO_JSON["Convert to<br/>JSON-serializable"]
        ENCODE["JSON encode"]
    end

    subgraph "Response"
        JSON_RESPONSE["JSON response<br/>to client"]
    end

    ROW --> TO_DICT
    TO_DICT --> TYPE_FIX
    TYPE_FIX --> ADD_META
    ADD_META --> TO_JSON
    TO_JSON --> ENCODE
    ENCODE --> JSON_RESPONSE
```

---

## Caching and Performance Flow

### Font Caching

```mermaid
graph TB
    subgraph "First Request"
        REQ1["get_font(path, 12)"]
        LOAD["Load from disk"]
        CACHE["Store in memory<br/>dict"]
        RETURN1["Return font"]
    end

    subgraph "Subsequent Requests"
        REQ2["get_font(path, 12)"]
        CHECK["Check cache"]
        HIT["Cache hit"]
        RETURN2["Return cached"]
    end

    subgraph "Cache Miss"
        LOAD2["Load from disk"]
        UPDATE["Update cache"]
        RETURN3["Return font"]
    end

    REQ1 --> LOAD
    LOAD --> CACHE
    CACHE --> RETURN1

    REQ2 --> CHECK
    CHECK --> HIT
    HIT --> RETURN2

    CHECK -->|miss| LOAD2
    LOAD2 --> UPDATE
    UPDATE --> RETURN3
```

### Database Query Optimization

```mermaid
graph TB
    subgraph "Query Plan"
        SQL["SELECT * FROM medicines<br/>WHERE time_window = 'morning'"]
        PLANNER["Query planner"]
    end

    subgraph "Optimization"
        OPTIONS["Option 1: Full table scan<br/>Option 2: Index scan<br/>Option 3: Index seek"]
        COST_CALC["Cost estimation"]
        SELECT["Select option 2<br/>(idx_medicines_time_window)"]
    end

    subgraph "Execution"
        SEEK["Use index to<br/>find matches"]
        FETCH["Fetch rows"]
        RETURN["Return results"]
    end

    SQL --> PLANNER
    PLANNER --> OPTIONS
    OPTIONS --> COST_CALC
    COST_CALC --> SELECT
    SELECT --> SEEK
    SEEK --> FETCH
    FETCH --> RETURN
```

---

## Summary

The data flows in the system are:

1. **Structured** - Clear entry and exit points
2. **Typed** - Data validation at boundaries
3. **Logged** - Error and activity logging throughout
4. **Efficient** - Caching and indexing for performance
5. **Reliable** - Transaction support and error recovery
6. **Scalable** - Patterns support growth in data volume

---

**See Also**:
- `/docs/ARCHITECTURE.md` - System architecture
- `/docs/DATABASE_SCHEMA.md` - Database design
- `/docs/COMPONENT_DIAGRAM.md` - Component relationships
- `/docs/API_DESIGN.md` - API specifications
