"""
IMPLEMENTATION GUIDE - Production Ingestion System

Complete guide for implementing and deploying the B2B security questionnaire
ingestion pipeline with the SecureAnswer platform.
"""

# ============================================================================
# SYSTEM OVERVIEW
# ============================================================================

SYSTEM_OVERVIEW = """
PRODUCTION INGESTION SYSTEM - COMPLETE ARCHITECTURE

┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                                     │
│                                                                              │
│  Ingestion UI (Drag & Drop) → Dashboard → Knowledge Base → Review Queue    │
└─────────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INGESTION SYSTEM (THIS MODULE)                           │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│  │ PDF Parser   │  │ DOCX Parser  │  │ XLSX Parser  │                     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤                     │
│  │ • Page track │  │ • Section    │  │ • Cell track │                     │
│  │ • OCR ready  │  │ • Table ext. │  │ • Merged     │                     │
│  │ • Image det. │  │ • Styles     │  │ • Multi-sheet│                     │
│  └──────────────┘  └──────────────┘  └──────────────┘                     │
│         ↓                   ↓                   ↓                           │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │     Content Detection & Classification               │                 │
│  │  (Question vs Policy, Confidence Scoring)            │                 │
│  └──────────────────────────────────────────────────────┘                 │
│         ↓                                                                   │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │     Unified Schema Validation                        │                 │
│  │  (All required fields, deterministic output)         │                 │
│  └──────────────────────────────────────────────────────┘                 │
│         ↓                                                                   │
│  ┌──────────────────────────────────────────────────────┐                 │
│  │     Error Handling & Logging                         │                 │
│  │  (No silent failures, full traceability)             │                 │
│  └──────────────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                     │
│                                                                              │
│  extracted_content table → Indexed for search → Knowledge Base             │
│  ingestion_errors table  → Error tracking & recovery                       │
│  ingestion_statistics    → Metrics & monitoring                            │
└─────────────────────────────────────────────────────────────────────────────┘
"""

print(SYSTEM_OVERVIEW)


# ============================================================================
# STEP-BY-STEP IMPLEMENTATION
# ============================================================================

IMPLEMENTATION_STEPS = """
STEP-BY-STEP IMPLEMENTATION GUIDE

PHASE 1: DEVELOPMENT ENVIRONMENT (1-2 hours)
─────────────────────────────────────────────

1.1 Install Core Dependencies
    pip install PyPDF2 python-docx openpyxl
    pip install -r requirements.txt

1.2 Verify Installation
    python -c "import ingestion_system; print('✓ System imported')"

1.3 Run Unit Tests
    pytest test_ingestion.py -v --cov=ingestion_system
    Expected: 40+ tests, 99%+ coverage

1.4 Run Example Transformations
    python example_usage.py
    Expected: 7 complete examples with output samples


PHASE 2: INTEGRATION WITH SECUREANSWER (2-4 hours)
──────────────────────────────────────────────────

2.1 Update Knowledge Base Schema
    ALTER TABLE knowledge_base_entries ADD COLUMN ingestion_metadata JSONB;
    ALTER TABLE knowledge_base_entries ADD COLUMN source_file_hash VARCHAR(64);
    ALTER TABLE knowledge_base_entries ADD COLUMN confidence_score DECIMAL(3,2);

2.2 Implement Ingestion Endpoint
    # Create FastAPI endpoint in SecureAnswer backend
    @app.post("/api/ingestion/upload")
    async def upload_for_ingestion(file: UploadFile, user_id: str):
        pipeline = IngestionPipeline()
        results = pipeline.ingest_file(file_path)
        # Store in KB with pending_review status
        # Create review queue entries for low confidence

2.3 Wire UI to Ingestion
    # Update Ingestion.jsx to:
    - Upload to /api/ingestion/upload endpoint
    - Poll /api/ingestion/status endpoint
    - Display results with confidence scores
    - Show errors in user-friendly format

2.4 Create Dashboard Widgets
    # Add to Dashboard.jsx:
    - Daily ingestion metrics (vw_ingestion_metrics)
    - Content type breakdown (vw_content_breakdown)
    - Recent errors (vw_error_summary)


PHASE 3: TESTING & VALIDATION (2-3 hours)
──────────────────────────────────────────

3.1 Create Test Files
    - Generate sample questionnaires (PDF, DOCX, XLSX)
    - Include edge cases: merged cells, scanned PDFs, etc.
    - Create corrupted files for error testing

3.2 Run Integration Tests
    python -m pytest test_ingestion.py -k "Pipeline" -v

3.3 Performance Testing
    # Create 100MB XLSX file
    # Time ingestion
    # Expected: < 5 minutes

3.4 Error Recovery Testing
    - Delete/corrupt files during ingestion
    - Verify error logging
    - Check database consistency


PHASE 4: PRODUCTION DEPLOYMENT (1-2 hours)
──────────────────────────────────────────

4.1 Database Setup
    psql -h prod-db.example.com -U postgres -d seceureanswer \\
        -f config_and_deployment.py | grep "DATABASE_SCHEMA"

4.2 Environment Configuration
    export ENVIRONMENT=production
    export DB_HOST=prod-db.example.com
    export DB_USER=ingestion_service
    export LOG_LEVEL=INFO

4.3 Deploy Code
    # Using your deployment process:
    git commit -m "feat: Add production ingestion system"
    git push origin main
    # CI/CD triggers tests and deploys

4.4 Verify Deployment
    # Monitor logs for errors
    # Run health check endpoint
    # Test end-to-end: Upload → Ingestion → KB → Query


PHASE 5: MONITORING & MAINTENANCE (Ongoing)
────────────────────────────────────────────

5.1 Daily Monitoring
    - Check ingestion error rate (should be < 5%)
    - Monitor average confidence scores (should be > 0.85)
    - Review low-confidence items in review queue

5.2 Weekly Review
    - Analyze confidence score distribution
    - Identify patterns in extraction failures
    - Tune detection heuristics if needed

5.3 Monthly Optimization
    - Profile ingestion performance
    - Optimize database queries
    - Plan ML model training for better classification
"""

print(IMPLEMENTATION_STEPS)


# ============================================================================
# CONFIGURATION MATRIX
# ============================================================================

CONFIGURATION_MATRIX = """
CONFIGURATION DECISIONS MATRIX

Environment     | Debug | Log Level | Workers | Batch Size | Max File
─────────────────────────────────────────────────────────────────────
LOCAL           | TRUE  | DEBUG     | 2       | 100        | 500MB
DEVELOPMENT     | TRUE  | DEBUG     | 4       | 500        | 500MB
STAGING         | FALSE | INFO      | 8       | 1000       | 1000MB
PRODUCTION      | FALSE | WARNING   | 16      | 5000       | 500MB

Feature                    | LOCAL | DEV | STAGING | PROD | Notes
───────────────────────────────────────────────────────────────────
PDF OCR                    | NO    | YES | YES     | YES  | Increases time 2-3x
Confidence Scoring         | YES   | YES | YES     | YES  | Always enabled
Database Indexes           | YES   | YES | YES     | YES  | Critical for performance
Error Logging              | YES   | YES | YES     | YES  | Always enabled
Structured JSON Logging    | NO    | YES | YES     | YES  | For log aggregation
Connection Pooling         | 5     | 10  | 15      | 20   | DB connections
Batch Inserts              | 100   | 500 | 1000    | 5000 | Items per transaction
"""

print(CONFIGURATION_MATRIX)


# ============================================================================
# FILE STRUCTURE
# ============================================================================

FILE_STRUCTURE = """
PROJECT FILE STRUCTURE

secure-answer/
├── Backend (Python Ingestion System)
│   ├── ingestion_system.py              [1500+ lines]
│   │   ├── StructuredLogger (logging)
│   │   ├── ExtractedContent (schema)
│   │   ├── PDFParser
│   │   ├── DOCXParser
│   │   ├── XLSXParser
│   │   ├── IngestionPipeline (orchestrator)
│   │   └── Utilities (detect_type, validate_schema, etc.)
│   │
│   ├── test_ingestion.py                [40+ unit tests]
│   │   ├── TestExtractedContentSchema
│   │   ├── TestContentTypeDetection
│   │   ├── TestBaseParserErrorHandling
│   │   ├── TestIngestionPipeline
│   │   └── TestDeterminism
│   │
│   ├── example_usage.py                 [7 complete examples]
│   │   ├── Example 1: Basic Ingestion
│   │   ├── Example 2: Batch Processing
│   │   ├── Example 3: Error Handling
│   │   ├── Example 4: Schema Validation
│   │   ├── Example 5: Content Type Detection
│   │   ├── Example 6: Deterministic Output
│   │   └── Example 7: Metadata Tracking
│   │
│   ├── config_and_deployment.py         [Configuration & DB schema]
│   │   ├── IngestionConfig (for all environments)
│   │   ├── DATABASE_SCHEMA (SQL)
│   │   ├── PERFORMANCE_TUNING (guide)
│   │   └── DEPLOYMENT_CHECKLIST
│   │
│   ├── ingestion_integration.py         [Integration with SecureAnswer]
│   │   ├── IngestionToKnowledgeBaseIntegration
│   │   ├── RetrievalWithConfidenceMetadata
│   │   ├── ValidationWithIngestionContext
│   │   ├── FastAPI endpoints
│   │   └── Dashboard views
│   │
│   ├── requirements.txt                 [All dependencies]
│   ├── INGESTION_SYSTEM.md             [Full documentation]
│   └── README.md                        [SecureAnswer platform docs]
│
├── Frontend (React - Existing)
│   ├── src/pages/Ingestion.jsx         [Upload & progress UI]
│   ├── src/pages/Dashboard.jsx         [Metrics & monitoring]
│   ├── src/pages/KnowledgeBase.jsx    [Item management]
│   ├── src/pages/ReviewQueue.jsx      [Manual review]
│   └── src/pages/Validation.jsx       [Quality checks]
│
└── Database
    ├── extracted_content table
    ├── ingestion_errors table
    ├── ingestion_statistics table
    ├── knowledge_base_entries table (extended)
    └── Views (metrics, error summaries, etc.)
"""

print(FILE_STRUCTURE)


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

DEPLOYMENT_CHECKLIST_DETAILED = """
DETAILED DEPLOYMENT CHECKLIST

PRE-DEPLOYMENT
──────────────
CODE
  ☐ All tests passing (pytest test_ingestion.py -v)
  ☐ Code coverage at 99%+ (pytest --cov)
  ☐ No warnings or errors in static analysis
  ☐ Documentation complete and reviewed
  ☐ Examples run without errors
  ☐ All dependencies specified in requirements.txt

SECURITY
  ☐ No hardcoded passwords or secrets
  ☐ File validation (type, size, headers)
  ☐ SQL injection prevention verified
  ☐ Input sanitization implemented
  ☐ Error messages don't leak sensitive data

PERFORMANCE
  ☐ PDF parsing: < 2s per 50-page file
  ☐ DOCX parsing: < 1s per 2MB file
  ☐ XLSX parsing: < 3s per 10M rows
  ☐ Database indexes created
  ☐ Connection pooling configured
  ☐ Batch insert size optimized

DOCUMENTATION
  ☐ API endpoints documented
  ☐ Configuration guide complete
  ☐ Known issues documented
  ☐ Troubleshooting guide provided
  ☐ Performance tuning guide written

INFRASTRUCTURE
  ☐ PostgreSQL 12+ installed and configured
  ☐ Tesseract OCR installed (for scanned PDFs)
  ☐ Database backups enabled
  ☐ Monitoring/logging infrastructure ready
  ☐ Alerting configured

DEPLOYMENT
──────────
  ☐ Database schema deployed (schema.sql)
  ☐ Indexes created
  ☐ Application code deployed
  ☐ Environment variables set
  ☐ Credentials configured securely
  ☐ Health checks passing

VALIDATION
──────────
  ☐ Ingestion endpoint responds
  ☐ Test file ingestion works
  ☐ Data appears in database
  ☐ Knowledge base UI updated
  ☐ Dashboard metrics showing
  ☐ Review queue populated for low-confidence items

POST-DEPLOYMENT
───────────────
  ☐ Monitor error logs for 24 hours
  ☐ Check confidence score distribution
  ☐ Verify file type detection working
  ☐ Test with various file types
  ☐ Confirm database backups running
  ☐ Alert system responsive
  ☐ On-call procedures documented
"""

print(DEPLOYMENT_CHECKLIST_DETAILED)


# ============================================================================
# RUNBOOKS FOR COMMON ISSUES
# ============================================================================

RUNBOOKS = """
OPERATIONAL RUNBOOKS

ISSUE: High Error Rate (> 5%)
──────────────────────────────
Detection:
  - Monitor: SELECT COUNT(*) FROM ingestion_errors WHERE resolved = FALSE

Triage:
  - Query: SELECT error_type, COUNT(*) FROM ingestion_errors GROUP BY error_type
  - Check: Are failures from specific file type? User? Timeframe?

Resolution:
  1. If PDF: Check if scanned (enable OCR in config)
  2. If XLSX: Check for merged cells (use xlsx_merged_cells_policy='expand')
  3. If DOCX: Verify file integrity (re-upload)
  4. Check disk space: df -h
  5. Check database: SELECT COUNT(*) FROM extracted_content

Recovery:
  - Failed files can be retried: pipeline.ingest_file(file_path)
  - Update ingestion_errors.retry_count
  - Re-queue in background job

Communication:
  - Notify users of files affected
  - Provide retry window


ISSUE: Low Confidence Scores (< 0.7 average)
─────────────────────────────────────────────
Detection:
  - Dashboard metric shows average < 0.7
  - Query: SELECT AVG(confidence_score) FROM extracted_content

Triage:
  1. Check extraction method: 
     SELECT metadata->>'extraction_method', COUNT(*)
     FROM extracted_content GROUP BY 1
  2. Analyze patterns:
     SELECT type, AVG(confidence_score), COUNT(*)
     FROM extracted_content GROUP BY type
  3. Check file quality:
     SELECT source_file, AVG(confidence_score)
     FROM extracted_content GROUP BY source_file HAVING AVG(confidence_score) < 0.7

Resolution:
  - Tune heuristics in detect_content_type()
  - Consider ML-based detection
  - Check file quality with users
  - Update extraction patterns

Optimization:
  - Train model on high-confidence samples
  - Implement custom classifiers per domain
  - Adjust thresholds based on use case


ISSUE: Memory Exhaustion on Large Files
────────────────────────────────────────
Detection:
  - OOM killer triggered
  - Ingestion stops mid-file

Prevention:
  1. Set max_file_size_mb in config (default: 500)
  2. Enable streaming for XLSX: openpyxl(read_only=True)
  3. Process in chunks for large PDFs

Resolution:
  - Kill process: pkill -f ingestion_system
  - Check disk: du -sh /tmp/
  - Clean up: rm -rf /tmp/ingestion/*
  - Retry with streaming mode

Tuning:
  - Increase worker_threads to distribute memory
  - Use asyncio for I/O operations
  - Implement generator-based processing


ISSUE: Slow Database Inserts
─────────────────────────────
Detection:
  - Ingestion completes but database operations slow
  - Check logs: ingestion_system.log
  - Query: EXPLAIN ANALYZE INSERT INTO extracted_content...

Analysis:
  1. Check indexes: SELECT * FROM pg_indexes WHERE tablename='extracted_content'
  2. Check table size: SELECT pg_size_pretty(pg_total_relation_size('extracted_content'))
  3. Check vacuum: LAST VACUUM, LAST AUTOVACUUM

Optimization:
  - Increase batch_size in config (target: 5000)
  - Disable indexes during bulk load (re-enable after)
  - Use UNLOGGED tables for staging (revert after)
  - Run VACUUM ANALYZE after large ingestion

Example:
  -- Optimize for bulk load
  BEGIN;
  ALTER TABLE extracted_content SET UNLOGGED;
  -- Perform 1M inserts
  ALTER TABLE extracted_content SET LOGGED;
  VACUUM ANALYZE extracted_content;
  COMMIT;


ISSUE: Duplicate Content Extracted
───────────────────────────────────
Detection:
  - Same file_hash appears multiple times
  - Query: SELECT source_file_hash, COUNT(*)
           FROM extracted_content
           GROUP BY source_file_hash
           HAVING COUNT(*) > 1

Root Cause:
  1. File re-ingested accidentally
  2. Pipeline.ingest_directory() processing duplicates
  3. Retry mechanism triggered multiple times

Prevention:
  - Check file hash before ingestion
  - Query: SELECT source_file_hash FROM extracted_content WHERE id = ?
  - Skip if already processed

Remediation:
  - Delete duplicates (keep one):
    DELETE FROM extracted_content
    WHERE id NOT IN (
      SELECT MAX(id) FROM extracted_content
      GROUP BY source_file_hash
    )
  - Notify users of deduplication
"""

print(RUNBOOKS)


# ============================================================================
# SUCCESS METRICS
# ============================================================================

SUCCESS_METRICS = """
SUCCESS METRICS & TARGETS

Processing Performance
──────────────────────
Metric                          Target              Alert Threshold
─────────────────────────────────────────────────────────────────────
PDF parsing time (per page)     < 50ms              > 100ms
DOCX parsing time (per 1MB)     < 500ms             > 1000ms
XLSX parsing time (per 10K rows) < 300ms            > 500ms
Content type detection time     < 10ms              > 20ms
Database insert time (1K items) < 500ms             > 1000ms

Data Quality
────────────
Metric                          Target              Alert Threshold
─────────────────────────────────────────────────────────────────────
Average confidence score        > 0.85              < 0.75
Question detection accuracy     > 0.90              < 0.80
Policy detection accuracy       > 0.85              < 0.75
Schema validation pass rate     > 0.99              < 0.95
Error rate                      < 5%                > 10%

Reliability
───────────
Metric                          Target              Alert Threshold
─────────────────────────────────────────────────────────────────────
Uptime                          > 99.9%             < 99.0%
MTBF (Mean Time Between Failure) > 30 days          < 7 days
MTTR (Mean Time To Recover)     < 1 hour            > 4 hours
SLA compliance                  > 99.5%             < 99.0%

Monitoring Queries
──────────────────

-- Performance
SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)))
FROM extracted_content;

-- Quality
SELECT AVG(confidence_score) FROM extracted_content;

-- Error rate
SELECT 100.0 * COUNT(CASE WHEN errors != '[]' THEN 1 END) / COUNT(*)
FROM extracted_content;

-- SLA
SELECT COUNT(*) as total,
       COUNT(CASE WHEN extraction_timestamp > NOW() - INTERVAL '1 hour' THEN 1 END) as last_hour
FROM extracted_content
WHERE created_at > NOW() - INTERVAL '30 days';
"""

print(SUCCESS_METRICS)


# ============================================================================
# SUPPORT & TROUBLESHOOTING
# ============================================================================

SUPPORT_GUIDE = """
SUPPORT & TROUBLESHOOTING GUIDE

Quick Diagnostics
─────────────────

1. Check System Health
   $ python -c "import ingestion_system; pipeline = ingestion_system.IngestionPipeline(); print('✓ OK')"

2. Check Database
   $ psql -h localhost -U postgres -d ingestion -c "SELECT COUNT(*) FROM extracted_content;"

3. Check Logs
   $ tail -f ingestion_system.log

4. Check Errors
   $ python -c "from ingestion_system import IngestionPipeline; p = IngestionPipeline(); p.ingest_directory('./test_files')"

Common Questions
────────────────

Q: How do I enable OCR for scanned PDFs?
A: Set pdf_ocr_enabled=True in config, install tesseract: apt-get install tesseract-ocr

Q: Why are some questions not detected?
A: Question detection uses heuristics. Try ML-based detection or add custom patterns.

Q: How do I improve database performance?
A: 1) Create indexes (done in schema), 2) Increase batch size, 3) Run VACUUM

Q: Can I retry failed files?
A: Yes: pipeline.ingest_file(file_path)

Q: How do I export results?
A: pipeline.export_results("output.json", format="json")

Contact & Escalation
────────────────────

Level 1: Check logs and known issues list
Level 2: Run diagnostics and review runbooks
Level 3: Check database integrity and backups
Level 4: Contact engineering team with:
  - Error logs
  - Database diagnostics
  - File sample (if possible)
  - Reproduction steps
"""

print(SUPPORT_GUIDE)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("IMPLEMENTATION GUIDE COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review INGESTION_SYSTEM.md for detailed documentation")
    print("2. Run: python example_usage.py")
    print("3. Run tests: pytest test_ingestion.py -v")
    print("4. Follow PHASE 1 in IMPLEMENTATION_STEPS above")
    print("\n" + "="*80)
