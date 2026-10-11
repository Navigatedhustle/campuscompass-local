# Architecture

React/TypeScript UI → FastAPI → canonical synthetic JSON and SQLite run state → scoped retrieval, local embeddings and reranking → local writer → deterministic claim release checks → ReportLab PDF and advisor review. Student/advisor permission checks precede retrieval and exports.

## Implemented endpoints inspected from source

| Method | Route | Source |
| --- | --- | --- |
| GET | `/api/accounts` | `app/main.py` |
| POST | `/api/session` | `app/main.py` |
| GET | `/api/students` | `app/main.py` |
| GET | `/api/students/{sid}/sources` | `app/main.py` |
| GET | `/api/students/{sid}/documents/{source_id}` | `app/main.py` |
| POST | `/api/runs` | `app/main.py` |
| GET | `/api/runs/{rid}` | `app/main.py` |
| GET | `/api/runs/{rid}/brief.pdf` | `app/main.py` |
| POST | `/api/runs/{rid}/review` | `app/main.py` |
| GET | `/api/health` | `app/main.py` |

These routes establish implementation shape. They do not establish successful provider integration or model quality. Generated state and data stores are excluded from the repository.
