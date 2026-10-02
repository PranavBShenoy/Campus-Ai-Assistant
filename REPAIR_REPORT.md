# CampusAI Repair Report

## Fixes

- Matched ChromaDB to the supplied persistent-store schema, preventing the `object of type 'int' has no len()` crash.
- Made vector cleanup tolerate Chroma result shapes and verified deletion against a copy of the supplied store.
- Corrected document processing to pass named arguments, return chunks consistently, compute the count once, and prevent delete/index races from restoring deleted documents or leaving vectors behind.
- Added deterministic Study Planner rescheduling around weekly off days and daily-hour limits, followed by strict server validation.
- Added validation for all-seven-days-off and exam dates before the plan start; matched these checks in the existing frontend flow.
- Updated the existing Next.js 14 and UUID dependencies to patched compatible releases without changing the UI architecture.

## Tests run

- Backend compile and import: **PASS**
- Document processor, Chroma add/search/delete, scalar-ID cleanup, Study Planner scheduling/validation: **PASS**
- Supplied Chroma database open/count and cleanup on an isolated copy: **PASS**
- API health/OpenAPI route smoke test: **PASS**
- Frontend production build (13 static pages): **PASS**

## Windows startup

```bat
start.bat
```

Or PowerShell:

```powershell
.\start.ps1
```
