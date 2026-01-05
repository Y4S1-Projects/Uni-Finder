# Degree Recommendation Service (FastAPI)

This service recommends Sri Lankan university degree programs based on:

- **Eligibility rules** (stream, subject prerequisites, optional z-score cutoff)
- **Semantic similarity** between student interests and program name (SentenceTransformer)
- **Ranking** combining eligibility + similarity

## Local dev

- Service URL: `http://127.0.0.1:5001`
- Health: `GET /health`

## Install (Windows)

```bash
cd degree-recommendation-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (Windows)

Recommended:

```bash
python main.py
```

Alternatives:

```bash
python run.py
```

```bash
run_dev.bat
```

Or run uvicorn explicitly:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5001
```

## Environment variables

This service loads settings from `degree-recommendation-service/.env`.

Minimum:

```env
PORT=5001
CORS_ORIGINS=http://localhost:3000
```

Optional (advanced):

- `DATA_DIR` (default: `data`) — where CSV/NPY files are read from
- `EMBEDDING_MODEL_NAME` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `MAX_RECOMMENDATIONS` (default: `5`) — used as a setting, but note: API accepts `max_results`

## API

### `POST /recommend`

Returns only eligible programs with lightweight fields.

Request body (`app/schemas/request.py`):

```json
{
	"student": {
		"stream": "Science",
		"subjects": ["Physics", "Chemistry", "Combined Mathematics"],
		"zscore": 1.2345,
		"interests": "Computer Science"
	},
	"district": "Colombo",
	"max_results": 5
}
```

Notes:

- `student.zscore` is optional; if omitted/null, the service will not enforce cutoff checks.
- `student.zscore` is validated by Pydantic to be within $[-3, 3]$.
- `max_results` is optional.

Response (actual runtime shape): an array of objects like:

```json
[
	{
		"degree_name": "...",
		"metadata": { "institute": "...", "faculty": "..." },
		"similarity": 0.8123,
		"score": 0.9062
	}
]
```

### `POST /recommend/debug`

Returns eligible + rejected programs with detailed reasoning.

Response (actual runtime shape):

```json
{
	"eligible_recommendations": [
		{
			"degree_name": "...",
			"stream_required": "Science",
			"subjects_required": ["Physics"],
			"metadata": { "institute": "..." },
			"student_stream": "Science",
			"student_subjects": ["Physics"],
			"student_zscore": 1.23,
			"district": "Colombo",
			"similarity": 0.8123,
			"eligibility": true,
			"reason": "Eligible (Matched '...' (confidence=0.91))",
			"score": 0.9062
		}
	],
	"rejected_programs": [
		{
			"degree_name": "...",
			"eligibility": false,
			"reason": "Stream mismatch",
			"similarity": 0.1023,
			"metadata": { "institute": "..." }
		}
	],
	"summary": {
		"total_programs": 100,
		"eligible_count": 10,
		"rejected_count": 90
	}
}
```

### `GET /health`

```json
{ "status": "ok" }
```

## How recommendations work (implementation detail)

The service flow is implemented in `app/pipelines/recommendation_pipeline.py`.

### 1) Load program catalog

- Loaded once and cached in memory by `app/repositories/program_repository.py`.
- Source file: `data/program_catalog.csv`.

Each row becomes a `DegreeProgram` (`app/domain/program.py`). The mapper is resilient to different column names (e.g. `degree_name` vs `Degree`) and also derives a stable `program_id` if missing.

### 2) Eligibility checks

Eligibility is computed per program in `app/engines/rules_engine.py`:

1. **Stream match**

   - If the program declares a stream and the student declares a stream, they must match (case-insensitive).

2. **Subject prerequisites**

   - If the program declares prerequisites, the student must include them.
   - Implementation uses set subtraction:
     - `missing = set(required_subjects) - set(student_subjects)`
   - This means subject strings must match exactly (including punctuation/spaces). If your UI uses different naming, you may need to normalize inputs.

3. **Cutoff (semantic match) + optional z-score filtering**
   - Cutoff data: `data/cutoff_marks_2024_2025.csv` loaded by `app/repositories/cutoff_repository.py`.
   - The program name in the catalog may not match the cutoff CSV exactly, so `app/engines/cutoff_matcher.py` performs a semantic match:
     - Embeds each cutoff program name once at startup.
     - Embeds the catalog program name and picks the best dot-product match.
     - Default threshold: `0.85`.

Z-score behavior:

- If cutoff cannot be resolved:
  - and `student.zscore` is `null`/omitted → still eligible (interest-based recommendation)
  - and `student.zscore` is provided → rejected (explicitly: cutoff unavailable)
- If cutoff exists and `student.zscore` is provided but below cutoff → rejected.

### 3) Similarity scoring

Similarity is computed in `app/engines/similarity_engine.py` using a SentenceTransformer model:

- Student text: `student.interests`
- Program text: `program.degree_name`
- Embeddings are normalized, so cosine similarity is the dot product.

Performance optimization:

- The pipeline attempts to load `data/embeddings.npy`.
- If present and its length matches the number of programs in the catalog, the service uses the precomputed program embeddings and only encodes the student interests per request.
- If missing/mismatched, it falls back to encoding program names on-the-fly.

### 4) Final ranking score

Ranking is implemented in `app/engines/ranking_engine.py`:

$$\text{score} = 0.5 \cdot \mathbb{1}_{eligible} + 0.5 \cdot similarity$$

Because the list is filtered to eligible programs first, scores for recommended items typically look like:

$$\text{score} = 0.5 + 0.5 \cdot similarity$$

Programs are sorted by descending `score`.

## Data files

Located in `degree-recommendation-service/data/`:

- `program_catalog.csv` — program list and metadata (required)
- `cutoff_marks_2024_2025.csv` — z-score cutoff table (required for z-score filtering)
- `embeddings.npy` — precomputed embeddings for each catalog row (optional but recommended)
- `metadata.json` — present, not currently used by the pipeline
- `New Microsoft Excel Worksheet.xlsx` — present, not used by the service

## Regenerating embeddings

If you update `data/program_catalog.csv`, regenerate `data/embeddings.npy`:

```bash
cd degree-recommendation-service
.venv\Scripts\activate
python scripts/generate_embeddings.py
```

The script embeds **only** the `degree_name` column and writes `embeddings.npy`. It expects a `degree_name` column.

## What is currently unused

These files exist but are not used in the current request flow:

- `app/engines/explanation_engine.py` (empty)
- `app/utils/text_processing.py` (empty)
- `app/schemas/response.py` (types are defined but routes return raw dict/list)

## Troubleshooting

- **Slow first request / large downloads**: the SentenceTransformer model may download on first run; ensure you have internet access once.
- **`embeddings.npy` mismatch**: if the catalog row count changes, regenerate embeddings.
- **Unexpected “Missing required subjects”**: subject matching is exact-string based; ensure the frontend uses the same names as the catalog prerequisites.
- **Cutoff not found**: semantic cutoff matching requires similarity >= `0.85` and a district entry in the cutoff CSV.
