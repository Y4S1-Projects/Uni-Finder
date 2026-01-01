@echo off
echo Creating Degree Recommendation Service structure...

REM Root folder
mkdir degree-recommendation-service
cd degree-recommendation-service

REM Root files
type nul > README.md
type nul > requirements.txt
type nul > .env
type nul > .gitignore
type nul > main.py

REM =========================
REM App Layer
REM =========================
mkdir app

REM app/api
mkdir app\api
type nul > app\api\__init__.py
type nul > app\api\recommend.py

REM app/core
mkdir app\core
type nul > app\core\__init__.py
type nul > app\core\config.py
type nul > app\core\paths.py
type nul > app\core\logging.py

REM app/domain
mkdir app\domain
type nul > app\domain\__init__.py
type nul > app\domain\student.py
type nul > app\domain\program.py

REM app/engines
mkdir app\engines
type nul > app\engines\__init__.py
type nul > app\engines\rules_engine.py
type nul > app\engines\similarity_engine.py
type nul > app\engines\ranking_engine.py
type nul > app\engines\explanation_engine.py

REM app/pipelines
mkdir app\pipelines
type nul > app\pipelines\__init__.py
type nul > app\pipelines\recommendation_pipeline.py

REM app/repositories
mkdir app\repositories
type nul > app\repositories\__init__.py
type nul > app\repositories\program_repository.py

REM app/schemas
mkdir app\schemas
type nul > app\schemas\__init__.py
type nul > app\schemas\request.py
type nul > app\schemas\response.py

REM app/services
mkdir app\services
type nul > app\services\__init__.py
type nul > app\services\recommendation_service.py

REM app/utils
mkdir app\utils
type nul > app\utils\__init__.py
type nul > app\utils\text_processing.py
type nul > app\utils\math_utils.py

REM =========================
REM Data
REM =========================
mkdir data
type nul > data\program_catalog.csv
type nul > data\embeddings.npy
type nul > data\metadata.json

REM =========================
REM Models
REM =========================
mkdir models
mkdir models\sbert

REM =========================
REM Scripts
REM =========================
mkdir scripts
type nul > scripts\generate_embeddings.py
type nul > scripts\validate_dataset.py

REM =========================
REM Tests
REM =========================
mkdir tests
type nul > tests\__init__.py
type nul > tests\test_rules_engine.py
type nul > tests\test_similarity_engine.py
type nul > tests\test_ranking_engine.py
type nul > tests\test_pipeline.py

REM =========================
REM Docs
REM =========================
mkdir docs
type nul > docs\architecture.md
type nul > docs\api_contract.md
type nul > docs\methodology.md

echo.
echo ✅ Degree Recommendation Service structure created successfully!
echo Location: %cd%
pause
