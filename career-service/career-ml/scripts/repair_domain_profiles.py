"""
Phase C: Domain-Specific Profile Repair — AI/ML & Game Development
===================================================================
Repairs two critical data gaps:
  1. AI/ML roles with missing or bad profiles
  2. Game Development roles with zero profiles

Strategy:
  - Add missing domain-specific skills to skills_v2.csv
  - Create expert-defined role profiles for underserved roles
  - Fix bad skill mappings (e.g. AI_ML_ENGINEER_INT with "network" skills)
  - Mark synthetic profiles with source="synthetic" for confidence tracking
  - Rebuild role_skill_matrix and enhanced profiles

Run from career-service/:
    python career-ml/scripts/repair_domain_profiles.py
"""

import csv
import json
import sys
from pathlib import Path
from collections import OrderedDict

# Resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent                          # career-ml/
SERVICE_DIR = ML_DIR.parent                         # career-service/
DATA_DIR = ML_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPANDED_DIR = DATA_DIR / "expanded"

SKILLS_CSV = EXPANDED_DIR / "skills_v2.csv"
ROLE_PROFILES_CSV = PROCESSED_DIR / "role_skill_profiles_v2_fixed.csv"
ROLE_METADATA_JSON = PROCESSED_DIR / "role_metadata.json"

# Output
OUTPUT_SKILLS_CSV = SKILLS_CSV  # Update in place
OUTPUT_PROFILES_CSV = ROLE_PROFILES_CSV  # Update in place

# ═══════════════════════════════════════════════════════════════════════
#  STEP 1: Define missing skills
# ═══════════════════════════════════════════════════════════════════════

# New skills to add (starting from SK1200 to avoid conflicts)
NEW_SKILLS = [
    # AI/ML Skills
    ("SK1200", "tensorflow",      "tensorflow,tf",                   "ai_ml",        "technical"),
    ("SK1201", "pytorch",         "pytorch,torch",                   "ai_ml",        "technical"),
    ("SK1202", "deep learning",   "deep learning,deep_learning",     "ai_ml",        "technical"),
    ("SK1203", "keras",           "keras",                           "ai_ml",        "technical"),
    ("SK1204", "scikit-learn",    "scikit-learn,sklearn,scikit",     "ai_ml",        "technical"),
    ("SK1205", "computer vision", "computer vision,cv",              "ai_ml",        "technical"),
    ("SK1206", "reinforcement learning", "reinforcement learning,rl","ai_ml",        "technical"),
    ("SK1207", "numpy",           "numpy",                           "ai_ml",        "technical"),
    ("SK1208", "pandas",          "pandas",                          "ai_ml",        "technical"),
    ("SK1209", "scipy",           "scipy",                           "ai_ml",        "technical"),
    ("SK1210", "model deployment","model deployment,mlops",          "ai_ml",        "technical"),
    ("SK1211", "data pipelines",  "data pipelines,etl pipelines",   "data_engineering","technical"),
    ("SK1212", "feature engineering","feature engineering",          "ai_ml",        "technical"),
    ("SK1213", "model training",  "model training,model optimization","ai_ml",      "technical"),
    ("SK1214", "experiment tracking","experiment tracking,mlflow,wandb","ai_ml",    "technical"),
    ("SK1215", "transformers",    "transformers,huggingface",        "ai_ml",        "technical"),
    ("SK1216", "llm",             "llm,large language model",        "ai_ml",        "technical"),
    ("SK1217", "neural networks", "neural networks,ann,cnn,rnn,lstm","ai_ml",       "technical"),
    ("SK1218", "statistics",      "statistics,statistical analysis", "data_science", "technical"),
    ("SK1219", "r programming",   "r,r programming,rstudio",        "data_science", "technical"),
    ("SK1220", "data visualization","data visualization,tableau,powerbi","data_science","technical"),
    ("SK1221", "jupyter",         "jupyter,jupyter notebook,colab",  "ai_ml",        "technical"),
    ("SK1222", "opencv",          "opencv",                          "ai_ml",        "technical"),
    ("SK1223", "spark",           "spark,pyspark,apache spark",      "data_engineering","technical"),
    # Game Development Skills
    ("SK1230", "unity",           "unity,unity3d,unity engine",      "game_dev",     "technical"),
    ("SK1231", "unreal engine",   "unreal,unreal engine,ue4,ue5",   "game_dev",     "technical"),
    ("SK1232", "c#",              "c#,csharp,c sharp",               "game_dev",     "technical"),
    ("SK1233", "c++",             "c++,cpp,cplusplus",               "game_dev",     "technical"),
    ("SK1234", "game design",     "game design,gameplay design",     "game_dev",     "technical"),
    ("SK1235", "shader programming","shader,shaders,hlsl,glsl",     "game_dev",     "technical"),
    ("SK1236", "opengl",          "opengl,vulkan,directx,dx11,dx12","game_dev",     "technical"),
    ("SK1237", "3d modeling",     "3d modeling,3d modelling,maya,blender","game_dev","technical"),
    ("SK1238", "game physics",    "game physics,physics engine,rigid body","game_dev","technical"),
    ("SK1239", "godot",           "godot,gdscript",                  "game_dev",     "technical"),
    ("SK1240", "gameplay programming","gameplay programming,gameplay systems","game_dev","technical"),
    ("SK1241", "game ai",         "game ai,pathfinding,behavior trees","game_dev",  "technical"),
    ("SK1242", "level design",    "level design,world building",     "game_dev",     "technical"),
    ("SK1243", "animation systems","animation systems,skeletal animation","game_dev","technical"),
    ("SK1244", "multiplayer networking","multiplayer networking,netcode","game_dev", "technical"),
    ("SK1245", "game optimization","game optimization,profiling,frame rate","game_dev","technical"),
    ("SK1246", "version control for games","perforce,p4,plastic scm","game_dev",    "technical"),
    ("SK1247", "game engine architecture","game engine,engine architecture","game_dev","technical"),
    ("SK1248", "rendering",       "rendering,rendering pipeline,ray tracing","game_dev","technical"),
    ("SK1249", "audio programming","audio programming,fmod,wwise",   "game_dev",    "technical"),
]


# ═══════════════════════════════════════════════════════════════════════
#  STEP 2: Define expert role profiles for missing roles
# ═══════════════════════════════════════════════════════════════════════
# Format: role_id -> list of (skill_id, importance, frequency)
# importance: 0.0–1.0 (core >= 0.3, supporting 0.1–0.3, optional < 0.1)
# frequency: simulated (0.0–1.0)

# Existing skill IDs we can reuse:
# SK004 python, SK003 sql, SK031 machine learning, SK091 artificial intelligence
# SK194 natural language processing, SK277 data science, SK177 data analysis
# SK034 algorithms, SK028 problem solving, SK009 git, SK020 linux
# SK029 docker, SK161 agile, SK041 software engineer, SK002 javascript
# SK001 java, SK004 python, SK013 rest, SK021 api
# SK211 games, SK134 graphics, SK285 programming

SYNTHETIC_PROFILES = {
    # ─── AI/ML Roles ───────────────────────────────────────────────
    "AI_ML_ENGINEER_INT": {
        # FIX: Replace the bad network-skills profile
        "title": "AI / ML Engineer (Entry Level)",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK031",  0.90, 0.9),   # machine learning
            ("SK1207", 0.80, 0.8),   # numpy
            ("SK1208", 0.75, 0.8),   # pandas
            ("SK1204", 0.70, 0.7),   # scikit-learn
            ("SK1202", 0.60, 0.6),   # deep learning
            ("SK1218", 0.55, 0.6),   # statistics
            ("SK034",  0.50, 0.5),   # algorithms
            ("SK1221", 0.45, 0.5),   # jupyter
            ("SK003",  0.40, 0.5),   # sql
            ("SK009",  0.35, 0.4),   # git
            ("SK028",  0.30, 0.4),   # problem solving
            ("SK1217", 0.25, 0.3),   # neural networks
            ("SK1200", 0.20, 0.3),   # tensorflow
            ("SK1201", 0.20, 0.3),   # pytorch
            ("SK020",  0.15, 0.2),   # linux
            ("SK177",  0.15, 0.2),   # data analysis
            ("SK091",  0.10, 0.2),   # artificial intelligence
        ],
    },
    "JR_ML_ENGINEER": {
        "title": "Junior ML Engineer",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK031",  0.95, 0.9),   # machine learning
            ("SK1202", 0.85, 0.8),   # deep learning
            ("SK1207", 0.80, 0.8),   # numpy
            ("SK1208", 0.75, 0.8),   # pandas
            ("SK1204", 0.70, 0.7),   # scikit-learn
            ("SK1200", 0.65, 0.6),   # tensorflow
            ("SK1201", 0.65, 0.6),   # pytorch
            ("SK1217", 0.60, 0.6),   # neural networks
            ("SK003",  0.55, 0.6),   # sql
            ("SK034",  0.50, 0.5),   # algorithms
            ("SK1218", 0.50, 0.5),   # statistics
            ("SK009",  0.45, 0.5),   # git
            ("SK1221", 0.40, 0.4),   # jupyter
            ("SK028",  0.40, 0.4),   # problem solving
            ("SK020",  0.35, 0.4),   # linux
            ("SK029",  0.25, 0.3),   # docker
            ("SK1210", 0.20, 0.2),   # model deployment
            ("SK1212", 0.20, 0.2),   # feature engineering
            ("SK177",  0.15, 0.2),   # data analysis
            ("SK013",  0.10, 0.1),   # rest
            ("SK021",  0.10, 0.1),   # api
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
    "ML_ENGINEER": {
        "title": "ML Engineer",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK031",  1.00, 1.0),   # machine learning
            ("SK1202", 0.90, 0.9),   # deep learning
            ("SK1200", 0.80, 0.8),   # tensorflow
            ("SK1201", 0.80, 0.8),   # pytorch
            ("SK1217", 0.75, 0.7),   # neural networks
            ("SK1207", 0.75, 0.7),   # numpy
            ("SK1208", 0.70, 0.7),   # pandas
            ("SK1204", 0.65, 0.7),   # scikit-learn
            ("SK034",  0.60, 0.6),   # algorithms
            ("SK003",  0.55, 0.6),   # sql
            ("SK1210", 0.50, 0.5),   # model deployment
            ("SK1212", 0.50, 0.5),   # feature engineering
            ("SK1213", 0.45, 0.5),   # model training
            ("SK029",  0.40, 0.4),   # docker
            ("SK009",  0.40, 0.4),   # git
            ("SK020",  0.35, 0.4),   # linux
            ("SK1218", 0.35, 0.4),   # statistics
            ("SK1214", 0.30, 0.3),   # experiment tracking
            ("SK013",  0.25, 0.3),   # rest
            ("SK021",  0.25, 0.3),   # api
            ("SK028",  0.25, 0.3),   # problem solving
            ("SK1221", 0.20, 0.2),   # jupyter
            ("SK161",  0.15, 0.2),   # agile
            ("SK1223", 0.15, 0.2),   # spark
            ("SK177",  0.10, 0.1),   # data analysis
        ],
    },
    "DATA_SCIENTIST_INT": {
        "title": "Data Scientist (Entry Level)",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK1218", 0.90, 0.9),   # statistics
            ("SK003",  0.80, 0.8),   # sql
            ("SK1208", 0.75, 0.8),   # pandas
            ("SK1207", 0.70, 0.7),   # numpy
            ("SK177",  0.65, 0.7),   # data analysis
            ("SK031",  0.60, 0.6),   # machine learning
            ("SK1204", 0.55, 0.6),   # scikit-learn
            ("SK1220", 0.50, 0.5),   # data visualization
            ("SK1221", 0.45, 0.5),   # jupyter
            ("SK034",  0.40, 0.4),   # algorithms
            ("SK009",  0.35, 0.4),   # git
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK277",  0.25, 0.3),   # data science
            ("SK020",  0.15, 0.2),   # linux
        ],
    },
    "JR_DATA_SCIENTIST": {
        "title": "Junior Data Scientist",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK003",  0.90, 0.9),   # sql
            ("SK1218", 0.85, 0.8),   # statistics
            ("SK031",  0.80, 0.8),   # machine learning
            ("SK1208", 0.75, 0.8),   # pandas
            ("SK1207", 0.70, 0.7),   # numpy
            ("SK177",  0.65, 0.7),   # data analysis
            ("SK1204", 0.60, 0.6),   # scikit-learn
            ("SK1220", 0.55, 0.6),   # data visualization
            ("SK1202", 0.45, 0.5),   # deep learning
            ("SK1221", 0.40, 0.4),   # jupyter
            ("SK034",  0.40, 0.4),   # algorithms
            ("SK009",  0.35, 0.4),   # git
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK277",  0.25, 0.3),   # data science
            ("SK1200", 0.15, 0.2),   # tensorflow
            ("SK020",  0.15, 0.2),   # linux
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
    "DATA_SCIENTIST": {
        "title": "Data Scientist",
        "skills": [
            ("SK004",  1.00, 1.0),   # python
            ("SK031",  0.95, 1.0),   # machine learning
            ("SK003",  0.90, 0.9),   # sql
            ("SK1218", 0.85, 0.9),   # statistics
            ("SK1208", 0.80, 0.8),   # pandas
            ("SK1207", 0.75, 0.8),   # numpy
            ("SK1204", 0.70, 0.7),   # scikit-learn
            ("SK177",  0.65, 0.7),   # data analysis
            ("SK1202", 0.60, 0.6),   # deep learning
            ("SK1220", 0.55, 0.6),   # data visualization
            ("SK034",  0.50, 0.5),   # algorithms
            ("SK1200", 0.45, 0.5),   # tensorflow
            ("SK1201", 0.40, 0.4),   # pytorch
            ("SK1212", 0.35, 0.4),   # feature engineering
            ("SK009",  0.35, 0.4),   # git
            ("SK1221", 0.30, 0.3),   # jupyter
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK1223", 0.25, 0.3),   # spark
            ("SK277",  0.20, 0.2),   # data science
            ("SK020",  0.20, 0.2),   # linux
            ("SK029",  0.15, 0.2),   # docker
            ("SK013",  0.10, 0.1),   # rest
            ("SK161",  0.10, 0.1),   # agile
        ],
    },

    # ─── Game Development Roles ────────────────────────────────────
    "JR_GAME_DEV": {
        "title": "Junior Game Developer",
        "skills": [
            ("SK1233", 1.00, 1.0),   # c++
            ("SK1232", 0.90, 0.9),   # c#
            ("SK1230", 0.85, 0.8),   # unity
            ("SK1240", 0.70, 0.7),   # gameplay programming
            ("SK034",  0.60, 0.6),   # algorithms
            ("SK1234", 0.55, 0.6),   # game design
            ("SK211",  0.50, 0.5),   # games
            ("SK009",  0.45, 0.5),   # git
            ("SK285",  0.40, 0.4),   # programming
            ("SK1238", 0.35, 0.4),   # game physics
            ("SK1241", 0.30, 0.3),   # game ai
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK1242", 0.25, 0.3),   # level design
            ("SK1237", 0.20, 0.2),   # 3d modeling
            ("SK1243", 0.15, 0.2),   # animation systems
        ],
    },
    "GAME_DEVELOPER": {
        "title": "Game Developer",
        "skills": [
            ("SK1233", 1.00, 1.0),   # c++
            ("SK1232", 0.95, 0.9),   # c#
            ("SK1230", 0.85, 0.9),   # unity
            ("SK1231", 0.80, 0.8),   # unreal engine
            ("SK1240", 0.75, 0.7),   # gameplay programming
            ("SK034",  0.65, 0.7),   # algorithms
            ("SK1234", 0.60, 0.6),   # game design
            ("SK1238", 0.55, 0.6),   # game physics
            ("SK1241", 0.50, 0.5),   # game ai
            ("SK211",  0.45, 0.5),   # games
            ("SK1235", 0.40, 0.4),   # shader programming
            ("SK1236", 0.40, 0.4),   # opengl
            ("SK009",  0.35, 0.4),   # git
            ("SK285",  0.35, 0.3),   # programming
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK1245", 0.25, 0.3),   # game optimization
            ("SK1243", 0.25, 0.3),   # animation systems
            ("SK1242", 0.20, 0.2),   # level design
            ("SK1244", 0.15, 0.2),   # multiplayer networking
            ("SK020",  0.10, 0.1),   # linux
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
    "GAME_DESIGNER": {
        "title": "Game Designer",
        "skills": [
            ("SK1234", 1.00, 1.0),   # game design
            ("SK1242", 0.90, 0.9),   # level design
            ("SK211",  0.85, 0.8),   # games
            ("SK1240", 0.70, 0.7),   # gameplay programming
            ("SK1230", 0.60, 0.6),   # unity
            ("SK1232", 0.55, 0.6),   # c#
            ("SK1241", 0.50, 0.5),   # game ai
            ("SK1238", 0.40, 0.4),   # game physics
            ("SK285",  0.35, 0.4),   # programming
            ("SK028",  0.35, 0.4),   # problem solving
            ("SK1237", 0.30, 0.3),   # 3d modeling
            ("SK1243", 0.25, 0.3),   # animation systems
            ("SK009",  0.20, 0.2),   # git
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
    "SENIOR_GAME_DEV": {
        "title": "Senior Game Developer",
        "skills": [
            ("SK1233", 1.00, 1.0),   # c++
            ("SK1232", 0.95, 1.0),   # c#
            ("SK1231", 0.90, 0.9),   # unreal engine
            ("SK1230", 0.85, 0.9),   # unity
            ("SK1240", 0.80, 0.8),   # gameplay programming
            ("SK1247", 0.75, 0.7),   # game engine architecture
            ("SK034",  0.70, 0.7),   # algorithms
            ("SK1235", 0.65, 0.7),   # shader programming
            ("SK1236", 0.60, 0.6),   # opengl
            ("SK1248", 0.60, 0.6),   # rendering
            ("SK1238", 0.55, 0.6),   # game physics
            ("SK1241", 0.50, 0.5),   # game ai
            ("SK1234", 0.50, 0.5),   # game design
            ("SK1245", 0.45, 0.5),   # game optimization
            ("SK211",  0.40, 0.4),   # games
            ("SK1244", 0.40, 0.4),   # multiplayer networking
            ("SK009",  0.35, 0.4),   # git
            ("SK028",  0.35, 0.4),   # problem solving
            ("SK285",  0.30, 0.3),   # programming
            ("SK1243", 0.30, 0.3),   # animation systems
            ("SK1249", 0.20, 0.2),   # audio programming
            ("SK020",  0.15, 0.2),   # linux
            ("SK029",  0.15, 0.2),   # docker
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
    "LEAD_GAME_DEV": {
        "title": "Lead Game Developer",
        "skills": [
            ("SK1233", 1.00, 1.0),   # c++
            ("SK1247", 0.95, 0.9),   # game engine architecture
            ("SK1231", 0.90, 0.9),   # unreal engine
            ("SK1230", 0.85, 0.9),   # unity
            ("SK1232", 0.85, 0.9),   # c#
            ("SK1240", 0.80, 0.8),   # gameplay programming
            ("SK1248", 0.70, 0.7),   # rendering
            ("SK1235", 0.65, 0.7),   # shader programming
            ("SK1236", 0.60, 0.6),   # opengl
            ("SK034",  0.60, 0.6),   # algorithms
            ("SK1245", 0.55, 0.6),   # game optimization
            ("SK1234", 0.50, 0.5),   # game design
            ("SK1238", 0.45, 0.5),   # game physics
            ("SK1241", 0.45, 0.5),   # game ai
            ("SK1244", 0.40, 0.4),   # multiplayer networking
            ("SK211",  0.35, 0.4),   # games
            ("SK009",  0.30, 0.3),   # git
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK285",  0.25, 0.3),   # programming
            ("SK161",  0.20, 0.2),   # agile
            ("SK1243", 0.20, 0.2),   # animation systems
            ("SK1249", 0.15, 0.2),   # audio programming
            ("SK020",  0.15, 0.2),   # linux
        ],
    },
    "TECHNICAL_GAME_DESIGNER": {
        "title": "Technical Game Designer",
        "skills": [
            ("SK1234", 1.00, 1.0),   # game design
            ("SK1240", 0.90, 0.9),   # gameplay programming
            ("SK1232", 0.80, 0.8),   # c#
            ("SK1230", 0.75, 0.8),   # unity
            ("SK1242", 0.70, 0.7),   # level design
            ("SK211",  0.65, 0.6),   # games
            ("SK1233", 0.60, 0.6),   # c++
            ("SK1241", 0.55, 0.6),   # game ai
            ("SK1238", 0.50, 0.5),   # game physics
            ("SK034",  0.45, 0.5),   # algorithms
            ("SK285",  0.40, 0.4),   # programming
            ("SK1243", 0.35, 0.4),   # animation systems
            ("SK1235", 0.30, 0.3),   # shader programming
            ("SK028",  0.30, 0.3),   # problem solving
            ("SK009",  0.25, 0.3),   # git
            ("SK1237", 0.20, 0.2),   # 3d modeling
            ("SK1245", 0.15, 0.2),   # game optimization
            ("SK161",  0.10, 0.1),   # agile
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════
#  STEP 3: Define domain confidence metadata updates
# ═══════════════════════════════════════════════════════════════════════
# Synthetic roles get low job_count (=0) to signal lower confidence

SYNTHETIC_ROLE_METADATA_UPDATES = {
    # AI/ML roles
    "AI_ML_ENGINEER_INT":    {"source": "synthetic_repair", "job_count": 0},
    "JR_ML_ENGINEER":        {"source": "synthetic_expert", "job_count": 0},
    "ML_ENGINEER":           {"source": "synthetic_expert", "job_count": 0},
    "DATA_SCIENTIST_INT":    {"source": "synthetic_expert", "job_count": 0},
    "JR_DATA_SCIENTIST":     {"source": "synthetic_expert", "job_count": 0},
    "DATA_SCIENTIST":        {"source": "synthetic_expert", "job_count": 0},
    # Game Dev roles (all)
    "JR_GAME_DEV":           {"source": "synthetic_expert", "job_count": 0},
    "GAME_DEVELOPER":        {"source": "synthetic_expert", "job_count": 0},
    "GAME_DESIGNER":         {"source": "synthetic_expert", "job_count": 0},
    "SENIOR_GAME_DEV":       {"source": "synthetic_expert", "job_count": 0},
    "LEAD_GAME_DEV":         {"source": "synthetic_expert", "job_count": 0},
    "TECHNICAL_GAME_DESIGNER":{"source": "synthetic_expert", "job_count": 0},
}


# ═══════════════════════════════════════════════════════════════════════
#  EXECUTION
# ═══════════════════════════════════════════════════════════════════════

def add_new_skills():
    """Add missing AI/ML and Game Dev skills to skills_v2.csv."""
    import pandas as pd
    skills = pd.read_csv(SKILLS_CSV)
    existing_ids = set(skills["skill_id"].values)

    new_rows = []
    for sid, name, aliases, category, stype in NEW_SKILLS:
        if sid not in existing_ids:
            new_rows.append({
                "skill_id": sid,
                "name": name,
                "aliases": aliases,
                "category": category,
                "type": stype,
            })

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        combined = pd.concat([skills, new_df], ignore_index=True)
        combined.to_csv(SKILLS_CSV, index=False)
        print(f"[add_skills] Added {len(new_rows)} new skills to {SKILLS_CSV.name}")
        print(f"[add_skills] Total skills: {len(combined)}")
    else:
        print("[add_skills] No new skills needed (all already exist)")

    return len(new_rows)


def update_role_profiles():
    """Add/replace synthetic role profiles."""
    import pandas as pd
    profiles = pd.read_csv(ROLE_PROFILES_CSV)

    # Load role titles from metadata
    with open(ROLE_METADATA_JSON) as f:
        meta = json.load(f)
    titles = {e["role_id"]: e["role_title"] for e in meta}

    # Load skill names
    skills = pd.read_csv(SKILLS_CSV)
    skill_names = dict(zip(skills["skill_id"], skills["name"]))

    total_added = 0
    total_replaced = 0

    for role_id, spec in SYNTHETIC_PROFILES.items():
        title = spec["title"]
        skill_list = spec["skills"]

        # Remove existing profile if any (for repair cases like AI_ML_ENGINEER_INT)
        existing = profiles[profiles["role_id"] == role_id]
        if len(existing) > 0:
            profiles = profiles[profiles["role_id"] != role_id]
            total_replaced += 1
            print(f"[profiles] Replacing {role_id} ({len(existing)} skills -> {len(skill_list)} skills)")
        else:
            total_added += 1
            print(f"[profiles] Adding NEW profile: {role_id} ({len(skill_list)} skills)")

        new_rows = []
        for skill_id, importance, frequency in skill_list:
            sname = skill_names.get(skill_id, skill_id)
            new_rows.append({
                "role_id": role_id,
                "skill_id": skill_id,
                "frequency": round(frequency, 4),
                "importance": round(importance, 4),
                "role_title": title,
                "skill_name": sname,
            })

        profiles = pd.concat([profiles, pd.DataFrame(new_rows)], ignore_index=True)

    profiles.to_csv(ROLE_PROFILES_CSV, index=False)
    print(f"\n[profiles] Added {total_added} new roles, replaced {total_replaced} roles")
    print(f"[profiles] Total rows: {len(profiles)}, Unique roles: {profiles['role_id'].nunique()}")
    return total_added, total_replaced


def update_v3_metadata():
    """Update role_metadata_v3.json with source and job_count for synthetic roles."""
    v3_path = PROCESSED_DIR / "role_metadata_v3.json"
    if v3_path.exists():
        with open(v3_path) as f:
            v3 = json.load(f)
    else:
        v3 = {}

    for role_id, updates in SYNTHETIC_ROLE_METADATA_UPDATES.items():
        if role_id not in v3:
            v3[role_id] = {}
        v3[role_id].update(updates)
        # Ensure domain is set
        if "domain" not in v3[role_id]:
            # Determine from metadata
            with open(ROLE_METADATA_JSON) as f:
                meta = json.load(f)
            for entry in meta:
                if entry["role_id"] == role_id:
                    v3[role_id]["domain"] = entry.get("domain", "")
                    break

    with open(v3_path, "w") as f:
        json.dump(v3, f, indent=2)
    print(f"[v3_metadata] Updated {len(SYNTHETIC_ROLE_METADATA_UPDATES)} entries in {v3_path.name}")


def rebuild_skill_matrix():
    """Rebuild the role_skill_matrix (pivot) from updated profiles."""
    import pandas as pd
    profiles = pd.read_csv(ROLE_PROFILES_CSV)

    skill_col = "skill_id"
    # Build pivot matrix
    matrix = profiles.pivot_table(
        index="role_id",
        columns=skill_col,
        values="importance",
        fill_value=0,
        aggfunc="max",
    )
    matrix_path = PROCESSED_DIR / "role_skill_matrix_v2_fixed.csv"
    matrix.to_csv(matrix_path)
    print(f"[rebuild] Saved role_skill_matrix: {matrix.shape[0]} roles × {matrix.shape[1]} skills")
    return matrix


def main():
    print("=" * 60)
    print("Phase C: Domain-Specific Profile Repair")
    print("=" * 60)

    print("\n── Step 1: Adding missing AI/ML & Game Dev skills ──")
    n_skills = add_new_skills()

    print("\n── Step 2: Adding/replacing role profiles ──")
    added, replaced = update_role_profiles()

    print("\n── Step 3: Updating v3 metadata with confidence flags ──")
    update_v3_metadata()

    print("\n── Step 4: Rebuilding skill matrix ──")
    rebuild_skill_matrix()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  New skills added:        {n_skills}")
    print(f"  New role profiles:       {added}")
    print(f"  Replaced role profiles:  {replaced}")
    print(f"  Domains affected:        AI_ML, DATA_SCIENCE, GAME_DEVELOPMENT")
    print("\nDone. Restart career-service to pick up changes.")


if __name__ == "__main__":
    # Ensure career-service is on path
    if str(SERVICE_DIR) not in sys.path:
        sys.path.insert(0, str(SERVICE_DIR))
    main()
