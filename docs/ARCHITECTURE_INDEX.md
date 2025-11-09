# Architecture Documentation Index

**Version:** 2.0.0
**Last Updated:** November 8, 2025
**Status:** Complete

---

## Overview

This index provides a comprehensive guide to the Pi Zero 2W Medicine Tracker architecture documentation. All documents use Mermaid diagrams for visual representation of system structure and data flows.

---

## Core Architecture Documents

### 1. **ARCHITECTURE.md** (18KB, 705 lines)
**Main system architecture overview**

Contains:
- System architecture diagram (layers and components)
- Core layer descriptions (presentation, application, API, data, utilities)
- Technology stack
- Module structure and hierarchies
- Communication patterns
- Deployment architecture (development and production)
- Design principles (SOLID, modularity, testability, performance)
- Data flow overview
- Future enhancement roadmap

**Key Diagrams**:
- System architecture (layer-based)
- Display module hierarchy
- Database module structure
- Shared utilities organization
- Deployment environments

**Best For**: Understanding the overall system structure and how components interact

---

### 2. **DATABASE_SCHEMA.md** (25KB, 952 lines)
**Complete database schema documentation**

Contains:
- Database overview and characteristics
- Schema entity-relationship diagram
- Table specifications (detailed column descriptions):
  - **medicines** - Medicine definitions with configuration
  - **medicine_days** - M2M relationship for scheduling
  - **tracking** - Adherence records
  - **time_windows** - Time slot definitions
  - **metadata** - System versioning
- Database views (3 views with usage examples)
- Triggers (automatic timestamp and metadata updates)
- Index strategy and performance considerations
- Constraint definitions
- Data type reference
- Example queries (7 common use cases)
- Maintenance procedures
- Performance characteristics and scalability limits

**Key Diagrams**:
- Entity-Relationship Diagram (ERD)
- Table relationships and constraints

**Best For**: Understanding data persistence, schema design, and database operations

---

### 3. **COMPONENT_DIAGRAM.md** (20KB, 769 lines)
**Component relationships and interactions**

Contains:
- Component overview and organization
- Core component relationships (display, database, API)
- Display component hierarchy (dependency tree)
- API component stack architecture
- Data flow between components
- Application integration patterns
- Complete dependency graph
- Component interaction examples (3 detailed scenarios)
- Component communication protocols
- Testing strategies (isolated and integration)
- Performance characteristics (latency and memory)

**Key Diagrams**:
- Component overview
- Display library dependency tree
- Database architecture
- API request/response flow
- Application integration patterns
- Complete dependency graph
- Test organization

**Best For**: Understanding how components interact and depend on each other

---

### 4. **DATA_FLOW.md** (24KB, 1057 lines)
**Data flow through the system**

Contains:
- High-level system data flow
- Medicine tracking flow (detailed sequence)
- API data flow (CRUD operations with sequences)
- Configuration management flow
- Touch input flow and coordinate mapping
- Display rendering pipeline
- Database operations (query execution, transactions)
- Backup and recovery flow
- Error handling flow (application and API)
- Data transformation pipeline (input validation, output serialization)
- Caching and performance optimization

**Key Diagrams**:
- Complete system data flow
- Medicine reminder sequence diagram
- Pending medicines retrieval flow
- Daily statistics calculation
- Create/Read/Update/Delete flows
- Touch event detection and handling
- Rendering pipeline
- Transaction flow
- Error handling and recovery
- Data transformation pipeline

**Best For**: Understanding how data moves through the system and processing sequences

---

## Quick Reference Guide

### Finding Information

**I want to understand...**

| Topic | Document | Section |
|-------|----------|---------|
| System structure | ARCHITECTURE.md | System Architecture, Core Layers |
| Database design | DATABASE_SCHEMA.md | Table Specifications, Views |
| Component dependencies | COMPONENT_DIAGRAM.md | Component Relationships, Dependency Graph |
| Data movement | DATA_FLOW.md | High-Level System Data Flow |
| API endpoints | API_DESIGN.md | (see existing docs) |
| Deployment | ARCHITECTURE.md | Deployment Architecture |
| Performance | COMPONENT_DIAGRAM.md | Performance Characteristics |
| Error handling | DATA_FLOW.md | Error Handling Flow |
| Touch input | DATA_FLOW.md | Touch Input Flow |
| Display rendering | DATA_FLOW.md | Display Rendering Flow |

---

## Document Statistics

| Document | Size | Lines | Tables | Diagrams | Code Examples |
|----------|------|-------|--------|----------|---------------|
| ARCHITECTURE.md | 18KB | 705 | 2 | 6 | 5 |
| DATABASE_SCHEMA.md | 25KB | 952 | 15 | 1 | 7 |
| COMPONENT_DIAGRAM.md | 20KB | 769 | 5 | 10 | 3 |
| DATA_FLOW.md | 24KB | 1057 | 2 | 16 | 2 |
| **TOTAL** | **87KB** | **3483** | **24** | **33** | **17** |

---

## Diagram Index

All diagrams in the architecture documentation use Mermaid format (rendered automatically on GitHub, GitLab, and other platforms).

### System-Level Diagrams

1. **System Architecture** (ARCHITECTURE.md)
   - Layers: Presentation, Application, API, Data
   - Components: Display, Touch, Web, Apps, Database

2. **Deployment Architecture** (ARCHITECTURE.md)
   - Development environment
   - Production environment (Pi Zero 2W)
   - Service architecture

### Component Diagrams

3. **Display Library Hierarchy** (COMPONENT_DIAGRAM.md)
   - Dependency tree of display components
   - Fonts, Canvas, Shapes, Text, Icons, Layouts, Components

4. **Database Architecture** (COMPONENT_DIAGRAM.md)
   - Connection management
   - Table relationships
   - Query interfaces

5. **API Stack** (COMPONENT_DIAGRAM.md)
   - Flask application factory
   - Blueprint organization
   - Route modules

### Data Flow Diagrams

6. **High-Level System Data Flow** (DATA_FLOW.md)
   - Input sources to output
   - Processing pipeline

7. **Medicine Tracking Flow** (DATA_FLOW.md)
   - Mark medicine taken sequence
   - Get pending medicines
   - Daily statistics calculation

8. **API CRUD Operations** (DATA_FLOW.md)
   - Create, Read, Update, Delete flows
   - Request validation and error handling

9. **Configuration Management** (DATA_FLOW.md)
   - Loading configuration
   - Updating settings
   - File format reference

10. **Touch Input Flow** (DATA_FLOW.md)
    - Event detection
    - Coordinate mapping

11. **Display Rendering** (DATA_FLOW.md)
    - Rendering pipeline
    - Component order
    - Refresh types (full vs partial)

12. **Database Operations** (DATA_FLOW.md)
    - Query execution flow
    - Transaction handling
    - Index usage

13. **Backup and Recovery** (DATA_FLOW.md)
    - Backup creation
    - Data recovery
    - JSON to SQLite migration

14. **Error Handling** (DATA_FLOW.md)
    - Application error flow
    - API error response flow

### Database Diagrams

15. **Entity-Relationship Diagram** (DATABASE_SCHEMA.md)
    - Tables: medicines, medicine_days, tracking, time_windows, metadata
    - Relationships and cardinality

---

## Cross-References

### ARCHITECTURE.md links to:
- DATABASE_SCHEMA.md - For detailed database structure
- COMPONENT_DIAGRAM.md - For component relationships
- DATA_FLOW.md - For detailed data flows
- API_DESIGN.md - For API specifications
- DEPLOYMENT_GUIDE.md - For deployment details

### DATABASE_SCHEMA.md links to:
- medicine_db.py - For implementation
- schema.sql - For raw SQL
- COMPONENT_DIAGRAM.md - For component relationships
- DATA_FLOW.md - For query examples

### COMPONENT_DIAGRAM.md links to:
- ARCHITECTURE.md - For system structure
- DATABASE_SCHEMA.md - For data persistence
- DATA_FLOW.md - For data movement

### DATA_FLOW.md links to:
- ARCHITECTURE.md - For system overview
- DATABASE_SCHEMA.md - For schema details
- COMPONENT_DIAGRAM.md - For component details
- API_DESIGN.md - For endpoint specifications

---

## How to Use These Documents

### For New Contributors

1. Start with **ARCHITECTURE.md** to understand the system structure
2. Read **COMPONENT_DIAGRAM.md** to see how components interact
3. Review **DATA_FLOW.md** to understand data movement
4. Consult **DATABASE_SCHEMA.md** for persistence details

### For Feature Development

1. Identify which components are affected (COMPONENT_DIAGRAM.md)
2. Check data flow implications (DATA_FLOW.md)
3. Review schema if data changes needed (DATABASE_SCHEMA.md)
4. Verify architectural compliance (ARCHITECTURE.md)

### For Debugging

1. Check error flow (DATA_FLOW.md - Error Handling)
2. Verify data flow (DATA_FLOW.md - Relevant operation)
3. Review component interaction (COMPONENT_DIAGRAM.md)
4. Check database state (DATABASE_SCHEMA.md)

### For Performance Optimization

1. Review performance characteristics (COMPONENT_DIAGRAM.md)
2. Check data flow efficiency (DATA_FLOW.md)
3. Review database indexes (DATABASE_SCHEMA.md)
4. Consider caching opportunities (DATA_FLOW.md - Caching)

### For Documentation Updates

1. Keep diagrams synchronized with code
2. Update examples when APIs change
3. Add new diagrams for new features
4. Review cross-references for consistency

---

## Documentation Standards

### Diagram Guidelines

- **Mermaid format** for all diagrams
- **Consistent styling** across documents
- **Clear labels** and descriptions
- **Legend** for complex diagrams
- **Directional flow** from left to right, top to bottom

### Code Examples

- Use actual code patterns from codebase
- Include error handling
- Show complete usage patterns
- Add comments for clarity

### Tables

- Use markdown tables
- Include type information
- Add constraint descriptions
- Provide usage notes

### Cross-References

- Link to related sections
- Use absolute paths for file references
- Link to relevant documentation
- Maintain bidirectional links

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-11-08 | Initial comprehensive documentation |

---

## Related Documentation

### Generated from Code Analysis
- `/docs/API_DESIGN.md` - RESTful API specification
- `/docs/API_ENDPOINT_INVENTORY.md` - Complete endpoint list
- `/docs/COMPONENT_LIBRARY_IMPLEMENTATION.md` - Display library details
- `/docs/DISPLAY_COMPONENTS.md` - UI component reference

### Deployment and Operations
- `/docs/DEPLOYMENT_GUIDE.md` - Deployment procedures
- `/docs/QUICK_REFERENCE.md` - Quick lookup guide

### Application-Specific
- Various app refactoring and summary documents

---

## Getting Started

To understand the Pi Zero 2W Medicine Tracker architecture:

1. **Read**: Start with ARCHITECTURE.md for the big picture
2. **Explore**: Use COMPONENT_DIAGRAM.md to understand relationships
3. **Trace**: Follow DATA_FLOW.md to see how data moves
4. **Reference**: Use DATABASE_SCHEMA.md for persistence details
5. **Navigate**: Use cross-references to explore deeper topics

---

## Feedback and Maintenance

These documents should be updated when:

1. **Architecture changes** - Update ARCHITECTURE.md and related diagrams
2. **Schema changes** - Update DATABASE_SCHEMA.md and ERD
3. **New components** - Update COMPONENT_DIAGRAM.md
4. **Data flow changes** - Update DATA_FLOW.md

---

**Document Format**: Markdown with embedded Mermaid diagrams
**Last Validated**: 2025-11-08
**Total Size**: 87KB
**Total Diagrams**: 33
**Total Code Examples**: 17

---

For questions or clarifications, refer to the specific document sections or the inline comments in the source code files.
