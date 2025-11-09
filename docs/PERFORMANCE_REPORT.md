# Pi Zero 2W Medicine Tracker - Performance Report

**Date:** 2025-11-08
**Status:** Performance Benchmarking Suite Ready
**Target Platform:** Raspberry Pi Zero 2W

## Executive Summary

This document outlines the performance benchmarking framework and optimization strategies for the Pi Zero 2W Medicine Tracker application. The system targets demanding performance metrics suitable for embedded systems with limited resources.

### Performance Targets

| Category | Target | Rationale |
|----------|--------|-----------|
| **API Responses** | <100ms | Real-time user interaction on Pi Zero |
| **Database Queries** | <50ms | SQLite optimization on limited hardware |
| **Display Renders** | <500ms | 2.13" e-ink display refresh rate |
| **Concurrent Users** | 50+ | Server load capacity |

---

## 1. Database Performance Benchmarking

### Benchmark Location
`tests/performance/benchmark_database.py`

### Test Coverage

#### 1.1 Basic Query Operations

```python
# Tests included:
- get_all_medicines()        # Retrieve all medicines
- get_medicine_by_id()       # Single medicine lookup
- get_pending_medicines()    # Medicines due now
- get_low_stock_medicines()  # Low stock detection
```

**Expected Results:**
- `get_medicine_by_id`: 2-5ms (indexed lookup)
- `get_all_medicines`: 10-20ms (50 medicines)
- `get_pending_medicines`: 5-10ms (time-based filter)
- `get_low_stock_medicines`: 5-10ms (stock filter)

#### 1.2 Write Operations

```python
# Tests included:
- mark_medicine_taken()      # Single dose tracking
- update_medicine()          # Medicine metadata update
- batch_mark_taken()         # Multiple dose tracking
```

**Expected Results:**
- `mark_medicine_taken`: 15-25ms (write + foreign key)
- `update_medicine`: 20-30ms (full record update)
- `batch_mark_taken`: 50-100ms (5 medicines)

#### 1.3 Complex Queries

```python
# Tests included:
- get_medicine_tracking_history()   # Historical data
- get_tracking_by_date_range()      # Date range queries
```

**Expected Results:**
- `get_tracking_by_date_range`: 20-40ms (30 days)
- `get_medicine_tracking_history`: 10-20ms (single medicine)

#### 1.4 Transaction Overhead

```python
# Tests included:
- transaction_overhead()     # Context manager overhead
```

**Expected Results:**
- Transaction overhead: <5ms (minimal overhead)

### Optimization Recommendations

#### Database Indexes
```sql
-- Recommended indexes for performance
CREATE INDEX idx_medicines_active ON medicines(active);
CREATE INDEX idx_medicines_low_stock ON medicines(low_stock_threshold, pills_remaining);
CREATE INDEX idx_tracking_date ON tracking(taken_date);
CREATE INDEX idx_tracking_medicine ON tracking(medicine_id);
CREATE INDEX idx_tracking_date_range ON tracking(medicine_id, taken_date);
```

#### Connection Pooling
- Use thread-local connections to reduce connection overhead
- Implement WAL (Write-Ahead Logging) mode for better concurrency
- Set appropriate timeout values (30 seconds recommended)

#### Query Optimization
```python
# Good: Use WHERE clause with indexed columns
medicines = db.get_pending_medicines(date.today())

# Bad: Load everything then filter in Python
medicines = [m for m in db.get_all_medicines() if m['active']]
```

#### Batch Operations
- Use batch_mark_taken() for 3+ medicines instead of individual calls
- Reduces transaction overhead by 60-70%
- Example: 5 medicines = ~80ms (vs 125ms for individual calls)

---

## 2. API Response Time Benchmarking

### Benchmark Location
`tests/performance/benchmark_api.py`

### Test Coverage

#### 2.1 GET Endpoints

| Endpoint | Target | Notes |
|----------|--------|-------|
| GET /api/v1/ | <50ms | Root info |
| GET /api/v1/health | <50ms | Health check |
| GET /api/v1/medicines | <75ms | List all |
| GET /api/v1/medicines/{id} | <50ms | Single lookup |
| GET /api/v1/medicines/pending | <75ms | Computed list |
| GET /api/v1/medicines/low-stock | <75ms | Computed list |

#### 2.2 POST Endpoints

| Endpoint | Target | Notes |
|----------|--------|-------|
| POST /api/v1/medicines | <100ms | Create medicine |
| POST /api/v1/medicines/{id}/take | <75ms | Mark taken |
| POST /api/v1/medicines/batch-take | <100ms | Batch mark |

#### 2.3 PUT/PATCH Endpoints

| Endpoint | Target | Notes |
|----------|--------|-------|
| PUT /api/v1/medicines/{id} | <100ms | Full update |
| PATCH /api/v1/medicines/{id} | <100ms | Partial update |

### Response Time Breakdown

```
GET /api/v1/medicines
├─ Database query (get_all_medicines): 15ms
├─ Serialization: 10ms
├─ JSON encoding: 5ms
├─ Flask overhead: 3ms
└─ Network: <2ms
   ────────────────
   Total: ~35ms

POST /api/v1/medicines/{id}/take
├─ JSON parsing: 2ms
├─ Validation: 3ms
├─ Database mark_taken: 20ms
├─ Database get_medicine: 5ms
├─ Serialization: 5ms
├─ Flask overhead: 3ms
└─ Network: <2ms
   ────────────────
   Total: ~40ms
```

### Optimization Recommendations

#### Request Handling
```python
# Good: Use efficient JSON serialization
from api.v1.serializers import serialize_medicine

# Bad: Inefficient Python dict manipulation
response = {'medicine': medicine.__dict__}
```

#### Caching Strategies
```python
# Cache static data (updated infrequently)
- Medicines list (cache for 60 seconds)
- Configuration (cache for 300 seconds)

# Don't cache
- Pending medicines (time-sensitive)
- Tracking data (frequently updated)
```

#### Async Operations (Future Enhancement)
```python
# For long-running operations
@app.route('/api/v1/reports/monthly', methods=['GET'])
async def generate_monthly_report():
    # Implement async report generation
    pass
```

---

## 3. Load Testing (Concurrent Users)

### Benchmark Location
`tests/performance/load_test.py`

### Test Scenarios

#### 3.1 Concurrent Users Test (50 users)

```
Scenario: 50 concurrent users × 10 requests each = 500 total requests

Expected Results:
├─ Total Duration: 5-10 seconds
├─ Requests/sec: 50-100 req/s
├─ Mean Response: <75ms
├─ P95 Response: <150ms
├─ P99 Response: <250ms
├─ Success Rate: >99%
└─ Zero errors expected
```

#### 3.2 Ramp-Up Test

```
Scenario: Gradually increase load to find breaking point

Stage 1: 10 users    → Expected: <50ms mean, 100% success
Stage 2: 25 users    → Expected: <75ms mean, 100% success
Stage 3: 50 users    → Expected: <100ms mean, 100% success
Stage 4: 100 users   → Expected: <150ms mean, 99%+ success
```

#### 3.3 Stress Test

```
Scenario: Push system beyond normal operating limits

Stage 1: 200 users   → Expected: <250ms mean, 95%+ success
Stage 2: 500 users   → Expected: <400ms mean, 90%+ success
```

### Expected vs. Actual Performance

| Load | Scenario | Expected | Actual | Status |
|------|----------|----------|--------|--------|
| 50 users | Concurrent | <100ms | - | To be measured |
| 100 users | Ramp-up | <150ms | - | To be measured |
| 200 users | Stress | <250ms | - | To be measured |
| 500 users | Stress | <400ms | - | To be measured |

### Bottleneck Identification

**Likely Bottlenecks on Pi Zero:**
1. **Database Connections** - Single-threaded SQLite
2. **Memory Limitations** - Limited RAM on Pi Zero
3. **CPU** - Single-core or dual-core limitations
4. **Network I/O** - Limited to Ethernet/WiFi

### Load Testing Recommendations

#### Connection Pooling
```python
# Use thread-local database connections
db = MedicineDatabase()  # Gets thread-local connection
```

#### Request Queuing
```python
# For high traffic scenarios
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

#### Horizontal Scaling (Future)
```python
# Multi-instance deployment with load balancer
# Using Docker + Compose or Kubernetes
```

---

## 4. Memory Usage Profiling

### Benchmark Location
`tests/performance/memory_profile.py`

### Profiling Areas

#### 4.1 Application Startup

```
API Startup Memory: ~50-80MB
├─ Flask framework: ~30-40MB
├─ Database connection: ~5-10MB
├─ Libraries loaded: ~20-30MB
└─ Idle application: ~50-80MB total
```

#### 4.2 Database Operations

```
Database Initialization: ~10-15MB
Creating 100 medicines: +20-30MB
Tracking 100 medicines × 30 days: +50-100MB
Total with data: ~150MB
```

#### 4.3 API Request Handling

```
50 API requests: ~20-40MB temporary
├─ Request parsing: ~1-2MB
├─ Database query: ~5-10MB
├─ Serialization: ~5-10MB
└─ Response transmission: ~5MB
```

#### 4.4 Concurrent Access

```
5 threads × 10 requests: ~40-60MB
├─ Thread-local storage: ~10MB per thread
├─ Connection objects: ~5MB per thread
└─ Request buffers: ~2-3MB per request
```

#### 4.5 Display Rendering

```
100 canvas creations: ~5-10MB
├─ PIL Image creation: ~3-5MB per 100
├─ Drawing context: ~1-2MB per 100
└─ Text rendering: <1MB
```

### Memory Leak Detection

```python
# Tools and techniques used:
- tracemalloc: Python memory tracking
- psutil: Process memory monitoring
- gc.collect(): Forced garbage collection

# Expected behavior:
- No memory growth over 1000 operations
- All temporary allocations freed after operation
- No dangling references
```

### Memory Optimization Recommendations

#### Pi Zero Constraints
```
Raspberry Pi Zero 2W Specifications:
- RAM: 512MB total
- Swap: Optional (0-2GB recommended)
- Storage: SD card (32GB+ recommended)

Application Target:
- API server: 100-150MB
- Database: 50-100MB
- Buffer: 200MB for requests
- OS/Other: ~200MB
────────────────────────
Total: ~500MB (within limits)
```

#### Optimization Strategies

1. **Image Optimization**
   ```python
   # Use lazy loading for images
   # Cache generated images
   # Compress images appropriately
   ```

2. **Database Caching**
   ```python
   # Cache frequently accessed medicines (60s TTL)
   # Use SQLite memory caching
   # Implement pagination (not load-all)
   ```

3. **Request/Response Optimization**
   ```python
   # Use streaming for large responses
   # Implement pagination
   # Compress responses with gzip
   ```

4. **Garbage Collection**
   ```python
   # Configure Python GC for embedded systems
   import gc
   gc.set_debug(0)  # Disable debug overhead
   gc.set_threshold(700, 10, 10)  # Tune for Pi Zero
   ```

---

## 5. Display Render Performance

### Benchmark Location
`tests/performance/benchmark_database.py` (Display section in memory_profile.py)

### Render Operations

#### 5.1 Canvas Creation

```
Target: <500ms for complex scenes

Canvas Size: 250×122 pixels (Waveshare 2.13" e-ink)
Mode: 1-bit (black and white)

Performance:
├─ create_canvas(): ~0.5ms
├─ PIL Image creation: ~0.3ms
└─ Drawing context: ~0.2ms
```

#### 5.2 Text Rendering

```
Target: <500ms per screen update

Text Operations:
├─ Single line: ~1ms
├─ 10 lines: ~10ms
└─ Complex layout: ~20-50ms
```

#### 5.3 Full Display Update

```
Target: <500ms per refresh

Typical Medicine List Display:
├─ Canvas creation: 1ms
├─ Background: 2ms
├─ 8 medicines (lines): 15ms
├─ Icons/decorations: 10ms
├─ Total: ~28ms
└─ Margin: <500ms target easily met
```

### Display Optimization

#### Partial Updates
```python
# Use partial display updates when possible
# Only update changed regions
# Reduces render time by 60-80%

epd.displayPartial(buffer)  # Faster than full
epd.display(buffer)         # Full update (slower)
```

#### Caching
```python
# Cache rendered components
# Redraw only changed sections
medicine_cache = {}

def render_medicine(med_id):
    if med_id in medicine_cache:
        return medicine_cache[med_id]
    rendered = generate_medicine_image(med_id)
    medicine_cache[med_id] = rendered
    return rendered
```

---

## 6. Running the Performance Tests

### Prerequisites
```bash
# Install performance testing dependencies
pip install -r requirements-test.txt

# Additional dependencies
pip install psutil memory-profiler
```

### Running Individual Benchmarks

#### Database Benchmarks
```bash
cd /home/user/pizerowgpio
python -m tests.performance.benchmark_database

# Output: .benchmarks/database_benchmark.json
```

#### API Benchmarks
```bash
python -m tests.performance.benchmark_api

# Output: .benchmarks/api_benchmark.json
```

#### Load Tests
```bash
python -m tests.performance.load_test

# Output: .benchmarks/load_test.json
```

#### Memory Profiling
```bash
python -m tests.performance.memory_profile

# Output: .benchmarks/memory_profile.json
```

### Running All Benchmarks
```bash
# Create comprehensive performance test suite
python -c "
import sys; sys.path.insert(0, '/home/user/pizerowgpio')
from tests.performance.benchmark_database import run_benchmarks as db_bench
from tests.performance.benchmark_api import run_benchmarks as api_bench
from tests.performance.load_test import run_load_tests
from tests.performance.memory_profile import run_memory_profiling

print('Running Database Benchmarks...')
db_bench()

print('\nRunning API Benchmarks...')
api_bench()

print('\nRunning Load Tests...')
run_load_tests()

print('\nRunning Memory Profiling...')
run_memory_profiling()
"
```

---

## 7. Performance Metrics Interpretation

### Database Query Times

| Operation | <25ms | 25-50ms | >50ms | Status |
|-----------|-------|---------|-------|--------|
| get_medicine_by_id | EXCELLENT | Good | Poor | Target: <50ms |
| get_pending_medicines | EXCELLENT | Good | Poor | Target: <50ms |
| mark_medicine_taken | EXCELLENT | Good | Poor | Target: <50ms |

### API Response Times

| Endpoint | <50ms | 50-100ms | >100ms | Status |
|----------|-------|----------|--------|--------|
| GET /medicines | EXCELLENT | Good | Poor | Target: <100ms |
| POST /medicines | Good | EXCELLENT | Poor | Target: <100ms |
| GET /health | EXCELLENT | Good | Poor | Target: <100ms |

### Load Test Success Metrics

```
50 Concurrent Users:
├─ Success Rate: Target >99%
├─ Mean Response: Target <100ms
├─ P95 Response: Target <150ms
└─ P99 Response: Target <250ms

100 Concurrent Users:
├─ Success Rate: Target >95%
├─ Mean Response: Target <150ms
├─ P95 Response: Target <250ms
└─ P99 Response: Target <400ms
```

---

## 8. Optimization Strategies

### Quick Wins (Easy, High Impact)

1. **Add Database Indexes** (5-10ms improvement)
   - Impact: All query operations
   - Effort: <1 hour
   - ROI: 20-30% faster queries

2. **Implement Query Result Caching** (10-20ms improvement)
   - Impact: Repeated queries
   - Effort: 2-3 hours
   - ROI: 30-40% faster for cache hits

3. **Optimize Serialization** (5-10ms improvement)
   - Impact: API response time
   - Effort: 1-2 hours
   - ROI: 15-20% faster responses

### Medium Effort (Moderate Impact)

4. **Connection Pooling** (5-10ms improvement)
   - Impact: Concurrent requests
   - Effort: 3-4 hours
   - ROI: 20% improvement under load

5. **Response Compression** (20-30% size reduction)
   - Impact: Network bandwidth
   - Effort: 2-3 hours
   - ROI: Faster downloads, reduced bandwidth

6. **Pagination** (50% improvement for large datasets)
   - Impact: List operations
   - Effort: 4-6 hours
   - ROI: Major improvement for scale

### Advanced Optimizations (Complex)

7. **Async API Handlers** (Not needed at 50 concurrent)
   - Consider only if needed for 200+ users
   - Effort: 8-10 hours
   - ROI: 30-40% under heavy load

8. **Database Replication** (Scalability)
   - Consider only for multi-instance setup
   - Effort: 16+ hours
   - ROI: High availability, load distribution

---

## 9. Continuous Performance Monitoring

### Recommended Setup

```python
# Add performance middleware to Flask
from api.v1.middleware import PerformanceMiddleware

app.wsgi_app = PerformanceMiddleware(app.wsgi_app)
```

### Metrics to Track

```
Daily Measurements:
├─ Database query latencies (min, max, p95, p99)
├─ API response times (by endpoint)
├─ Memory usage (peak, average)
├─ Error rates
└─ Concurrent user capacity
```

### Alert Thresholds

```
Database Queries:
├─ Alert if p95 > 100ms (normally <50ms)
├─ Alert if mean > 75ms (normally <40ms)

API Response:
├─ Alert if p95 > 200ms (normally <150ms)
├─ Alert if mean > 125ms (normally <100ms)

Memory:
├─ Alert if usage > 400MB (normally 100-200MB)
├─ Alert if growth rate > 10MB/hour
```

---

## 10. Performance Optimization Checklist

- [ ] Database indexes created and verified
- [ ] Query optimization completed
- [ ] Caching strategy implemented
- [ ] Connection pooling enabled
- [ ] Response compression enabled
- [ ] Pagination implemented for large datasets
- [ ] Memory leaks checked with tracemalloc
- [ ] Display rendering optimized with partial updates
- [ ] Load testing completed (50+ users)
- [ ] Performance monitoring setup
- [ ] Documentation updated with results
- [ ] Benchmarks added to CI/CD pipeline

---

## 11. Troubleshooting Performance Issues

### High API Response Times

1. **Check database query times first**
   ```bash
   python -m tests.performance.benchmark_database
   ```

2. **Enable query logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Profile slow endpoints**
   ```bash
   python -m tests.performance.benchmark_api
   ```

4. **Check memory usage**
   ```bash
   python -m tests.performance.memory_profile
   ```

### High Memory Usage

1. **Check for memory leaks**
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... operations ...
   current, peak = tracemalloc.get_traced_memory()
   print(f"Peak: {peak / 1024 / 1024}MB")
   ```

2. **Profile memory hotspots**
   - Run memory_profile.py
   - Check RSS delta per operation
   - Identify largest allocations

3. **Optimize known issues**
   - Reduce response payload sizes
   - Implement pagination
   - Cache frequently accessed data

### Load Testing Failures

1. **Check concurrent connection handling**
   ```bash
   python -m tests.performance.load_test
   ```

2. **Monitor resource usage during load**
   ```bash
   watch -n 1 'ps aux | grep python'
   ```

3. **Check database concurrency settings**
   ```python
   db._get_connection().execute("PRAGMA journal_mode = WAL")
   ```

---

## 12. Conclusion

The Pi Zero 2W Medicine Tracker application is designed to meet strict performance targets suitable for embedded systems. By following the optimization recommendations and maintaining performance visibility through regular benchmarking, the system will continue to meet its performance goals as it scales.

### Key Success Factors

1. **Database Optimization** - Critical for responsive UI
2. **Memory Management** - Limited resources require careful handling
3. **Concurrent User Handling** - Must support 50+ concurrent requests
4. **Display Performance** - Must refresh quickly and responsively

### Next Steps

1. Run the complete benchmark suite
2. Document actual performance metrics
3. Identify and prioritize optimizations
4. Implement quick wins first
5. Monitor performance in production
6. Plan advanced optimizations as needed

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Status:** Ready for Testing
