#!/usr/bin/env python3
"""
=============================================================================
AUTOFIX DATA PIPELINE - Career Recommendation System Data Alignment Tool
=============================================================================

A comprehensive script that automatically diagnoses and fixes ALL data alignment
issues in the career recommendation system data pipeline.

Usage:
    python autofix_data_pipeline.py                    # Run full fix
    python autofix_data_pipeline.py --dry-run          # Show issues without fixing
    python autofix_data_pipeline.py --validate-only    # Run diagnostics only
    python autofix_data_pipeline.py --backup-only      # Create backups only

Author: Career Service Pipeline Team
Version: 2.0.0
"""

import os
import sys
import re
import json
import shutil
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
from dataclasses import dataclass, field

import pandas as pd
import numpy as np

# Try to import joblib - used for model serialization
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    print("WARNING: joblib not installed. Model operations will be limited.")

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class PipelineConfig:
    """Configuration for the data pipeline paths and expected values."""
    # Root directory
    root_dir: Path = field(default_factory=lambda: Path(__file__).parent)
    
    # Data paths (relative to root_dir)
    skills_csv: str = "data/expanded/skills_v2.csv"
    jobs_csv: str = "data/processed/jobs_tagged_v2.csv"
    vectors_csv: str = "data/processed/job_skill_vectors_v2.csv"
    profiles_csv: str = "data/processed/role_skill_profiles_v2.csv"
    ladders_json: str = "data/processed/career_ladders_v2.json"
    model_pkl: str = "models/role_classifier_v2.pkl"
    columns_pkl: str = "models/skill_columns_v2.pkl"
    
    # Expected values
    expected_skill_count: int = 1147
    expected_job_count: int = 15230
    skill_id_pattern: str = r"^SK\d{3,4}$"  # SK001 to SK9999
    
    # Backup settings
    backup_dir: str = "backups"
    
    def get_path(self, name: str) -> Path:
        """Get full path for a named file."""
        return self.root_dir / getattr(self, name)


# =============================================================================
# ISSUE TRACKING
# =============================================================================

@dataclass
class Issue:
    """Represents a data alignment issue."""
    severity: str  # "CRITICAL" or "WARNING"
    category: str  # e.g., "skill_id", "vector", "model"
    file: str
    description: str
    details: Optional[str] = None
    fixable: bool = True
    
    def __str__(self) -> str:
        status = "✓ FIXABLE" if self.fixable else "✗ MANUAL FIX REQUIRED"
        return f"[{self.severity}] {self.category}: {self.description} ({status})"


class IssueTracker:
    """Tracks all discovered issues during diagnostics."""
    
    def __init__(self):
        self.issues: List[Issue] = []
        self.stats = {
            "CRITICAL": 0,
            "WARNING": 0,
            "files_scanned": 0,
            "fixes_applied": 0
        }
    
    def add(self, severity: str, category: str, file: str, 
            description: str, details: str = None, fixable: bool = True):
        """Add a new issue."""
        issue = Issue(severity, category, file, description, details, fixable)
        self.issues.append(issue)
        self.stats[severity] += 1
        return issue
    
    def critical(self, category: str, file: str, description: str, 
                 details: str = None, fixable: bool = True):
        """Add a critical issue."""
        return self.add("CRITICAL", category, file, description, details, fixable)
    
    def warning(self, category: str, file: str, description: str,
                details: str = None, fixable: bool = True):
        """Add a warning issue."""
        return self.add("WARNING", category, file, description, details, fixable)
    
    def get_by_category(self, category: str) -> List[Issue]:
        """Get all issues in a category."""
        return [i for i in self.issues if i.category == category]
    
    def get_critical(self) -> List[Issue]:
        """Get all critical issues."""
        return [i for i in self.issues if i.severity == "CRITICAL"]
    
    def get_fixable(self) -> List[Issue]:
        """Get all fixable issues."""
        return [i for i in self.issues if i.fixable]
    
    def has_critical(self) -> bool:
        """Check if there are any critical issues."""
        return self.stats["CRITICAL"] > 0
    
    def summary(self) -> str:
        """Get a summary of all issues."""
        lines = [
            "=" * 60,
            "ISSUE SUMMARY",
            "=" * 60,
            f"Total Issues Found: {len(self.issues)}",
            f"  - CRITICAL: {self.stats['CRITICAL']}",
            f"  - WARNING: {self.stats['WARNING']}",
            f"  - Files Scanned: {self.stats['files_scanned']}",
            f"  - Fixes Applied: {self.stats['fixes_applied']}",
            "=" * 60,
        ]
        return "\n".join(lines)


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(config: PipelineConfig, verbose: bool = True) -> logging.Logger:
    """Set up logging to both file and console."""
    log_file = config.root_dir / "autofix_pipeline.log"
    
    # Create logger
    logger = logging.getLogger("autofix_pipeline")
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler - detailed logging
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(file_format)
    logger.addHandler(fh)
    
    # Console handler - summary logging
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO if verbose else logging.WARNING)
    console_format = logging.Formatter('%(levelname)-8s | %(message)s')
    ch.setFormatter(console_format)
    logger.addHandler(ch)
    
    return logger


# =============================================================================
# DIAGNOSTIC FUNCTIONS
# =============================================================================

class DataDiagnostics:
    """Runs comprehensive diagnostics on all data files."""
    
    def __init__(self, config: PipelineConfig, tracker: IssueTracker, 
                 logger: logging.Logger):
        self.config = config
        self.tracker = tracker
        self.logger = logger
        self.data_cache: Dict[str, Any] = {}
    
    def load_file(self, name: str) -> Optional[Any]:
        """Load a data file, caching the result."""
        if name in self.data_cache:
            return self.data_cache[name]
        
        path = self.config.get_path(name)
        
        if not path.exists():
            self.tracker.critical(
                "file_missing", str(path),
                f"Required file not found: {path.name}",
                fixable=False
            )
            return None
        
        try:
            if name.endswith('_csv'):
                data = pd.read_csv(path)
            elif name.endswith('_json'):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif name.endswith('_pkl'):
                if HAS_JOBLIB:
                    data = joblib.load(path)
                else:
                    self.tracker.warning(
                        "dependency", str(path),
                        "joblib not available - cannot load pickle files"
                    )
                    return None
            else:
                self.logger.warning(f"Unknown file type: {name}")
                return None
            
            self.data_cache[name] = data
            self.tracker.stats["files_scanned"] += 1
            return data
            
        except Exception as e:
            self.tracker.critical(
                "file_error", str(path),
                f"Error loading file: {str(e)}",
                fixable=False
            )
            return None
    
    def run_all_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic checks and return results."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING DIAGNOSTIC CHECKS")
        self.logger.info("=" * 60)
        
        results = {}
        
        # 1. Check Skill ID Format
        self.logger.info("\n[1/5] Checking Skill ID Format...")
        results["skill_ids"] = self.check_skill_id_format()
        
        # 2. Check Skill Count Consistency
        self.logger.info("\n[2/5] Checking Skill Count Consistency...")
        results["skill_counts"] = self.check_skill_count_consistency()
        
        # 3. Check Vector Column Alignment
        self.logger.info("\n[3/5] Checking Vector Column Alignment...")
        results["vector_alignment"] = self.check_vector_column_alignment()
        
        # 4. Check Job-Skill Mapping
        self.logger.info("\n[4/5] Checking Job-Skill Mapping...")
        results["job_skill_mapping"] = self.check_job_skill_mapping()
        
        # 5. Check Model Compatibility
        self.logger.info("\n[5/5] Checking Model Compatibility...")
        results["model_compatibility"] = self.check_model_compatibility()
        
        return results
    
    def check_skill_id_format(self) -> Dict[str, Any]:
        """
        Check all skill IDs are in correct format: SK001, SK002, ..., SK1147
        Checks for: lowercase, missing padding, whitespace, duplicates, gaps
        """
        result = {
            "valid": True,
            "issues": [],
            "invalid_ids": [],
            "duplicates": [],
            "gaps": [],
            "whitespace_issues": [],
            "case_issues": []
        }
        
        skills_df = self.load_file("skills_csv")
        if skills_df is None:
            result["valid"] = False
            return result
        
        # Check for skill_id column
        if "skill_id" not in skills_df.columns:
            self.tracker.critical(
                "skill_id", "skills_v2.csv",
                "Missing 'skill_id' column in skills file"
            )
            result["valid"] = False
            return result
        
        skill_ids = skills_df["skill_id"].astype(str).tolist()
        seen = set()
        id_pattern = re.compile(r"^SK(\d+)$")
        
        for idx, skill_id in enumerate(skill_ids, 1):
            original = skill_id
            
            # Check for whitespace
            if skill_id != skill_id.strip():
                result["whitespace_issues"].append((idx, original))
                self.tracker.warning(
                    "skill_id", "skills_v2.csv",
                    f"Whitespace in skill ID at row {idx}: '{original}'"
                )
            
            skill_id = skill_id.strip()
            
            # Check for case issues
            if skill_id != skill_id.upper():
                result["case_issues"].append((idx, original))
                self.tracker.warning(
                    "skill_id", "skills_v2.csv",
                    f"Lowercase skill ID at row {idx}: '{original}'"
                )
            
            skill_id_upper = skill_id.upper()
            
            # Check format
            match = id_pattern.match(skill_id_upper)
            if not match:
                result["invalid_ids"].append((idx, original))
                self.tracker.critical(
                    "skill_id", "skills_v2.csv",
                    f"Invalid skill ID format at row {idx}: '{original}'",
                    "Expected format: SK### (e.g., SK001, SK1147)"
                )
                result["valid"] = False
            else:
                # Check for zero-padding (should be at least 3 digits)
                num_str = match.group(1)
                if len(num_str) < 3:
                    result["invalid_ids"].append((idx, original))
                    self.tracker.warning(
                        "skill_id", "skills_v2.csv",
                        f"Skill ID needs zero-padding at row {idx}: '{original}'",
                        f"Should be SK{num_str.zfill(3)}"
                    )
            
            # Check for duplicates
            if skill_id_upper in seen:
                result["duplicates"].append((idx, skill_id_upper))
                self.tracker.critical(
                    "skill_id", "skills_v2.csv",
                    f"Duplicate skill ID at row {idx}: '{skill_id_upper}'"
                )
                result["valid"] = False
            seen.add(skill_id_upper)
        
        # Check for gaps in sequence
        expected_ids = {f"SK{i:03d}" for i in range(1, self.config.expected_skill_count + 1)}
        # Also check for 4-digit IDs if skill count > 999
        if self.config.expected_skill_count > 999:
            expected_ids.update({f"SK{i:04d}" for i in range(1000, self.config.expected_skill_count + 1)})
        
        actual_ids = {sid.upper().strip() for sid in skill_ids}
        
        # Normalize both sets - handle both SK001 and SK0001 as valid
        def normalize_skill_id(sid: str) -> int:
            match = re.match(r"SK0*(\d+)", sid.upper())
            return int(match.group(1)) if match else -1
        
        actual_nums = {normalize_skill_id(sid) for sid in actual_ids if normalize_skill_id(sid) > 0}
        expected_nums = set(range(1, self.config.expected_skill_count + 1))
        
        missing_nums = expected_nums - actual_nums
        if missing_nums:
            result["gaps"] = sorted(missing_nums)[:10]  # Show first 10
            self.tracker.warning(
                "skill_id", "skills_v2.csv",
                f"Missing skill IDs in sequence: {len(missing_nums)} gaps found",
                f"First few: SK{result['gaps'][0]:03d}, SK{result['gaps'][1]:03d}..." if len(result['gaps']) > 1 else None
            )
        
        if result["valid"]:
            self.logger.info("  ✓ All skill IDs are valid")
        else:
            self.logger.error(f"  ✗ Found {len(result['invalid_ids'])} invalid skill IDs")
        
        return result
    
    def check_skill_count_consistency(self) -> Dict[str, Any]:
        """
        Check that skill counts are consistent across all files:
        - skills_v2.csv count = 1147
        - vector columns = 1147
        - model features = 1147
        """
        result = {
            "valid": True,
            "counts": {},
            "mismatches": []
        }
        
        expected = self.config.expected_skill_count
        
        # Check skills_v2.csv
        skills_df = self.load_file("skills_csv")
        if skills_df is not None:
            count = len(skills_df)
            result["counts"]["skills_csv"] = count
            if count != expected:
                self.tracker.critical(
                    "skill_count", "skills_v2.csv",
                    f"Skill count mismatch: {count} vs expected {expected}"
                )
                result["valid"] = False
                result["mismatches"].append(("skills_csv", count, expected))
            else:
                self.logger.info(f"  ✓ skills_v2.csv: {count} skills")
        
        # Check vector columns
        vectors_df = self.load_file("vectors_csv")
        if vectors_df is not None:
            skill_cols = [c for c in vectors_df.columns if c.startswith("skill_")]
            count = len(skill_cols)
            result["counts"]["vectors_columns"] = count
            if count != expected:
                self.tracker.critical(
                    "skill_count", "job_skill_vectors_v2.csv",
                    f"Vector columns mismatch: {count} vs expected {expected}"
                )
                result["valid"] = False
                result["mismatches"].append(("vectors_columns", count, expected))
            else:
                self.logger.info(f"  ✓ job_skill_vectors_v2.csv: {count} skill columns")
        
        # Check model columns
        if HAS_JOBLIB:
            model_cols = self.load_file("columns_pkl")
            if model_cols is not None:
                count = len(model_cols)
                result["counts"]["model_columns"] = count
                if count != expected:
                    self.tracker.critical(
                        "skill_count", "skill_columns_v2.pkl",
                        f"Model columns mismatch: {count} vs expected {expected}"
                    )
                    result["valid"] = False
                    result["mismatches"].append(("model_columns", count, expected))
                else:
                    self.logger.info(f"  ✓ skill_columns_v2.pkl: {count} columns")
        
        return result
    
    def check_vector_column_alignment(self) -> Dict[str, Any]:
        """
        Check vector columns are correctly aligned:
        - Expected: [skill_sk001, skill_sk002, ..., skill_sk1147]
        - Sorted in proper numeric order
        - All lowercase
        """
        result = {
            "valid": True,
            "missing_columns": [],
            "extra_columns": [],
            "wrong_order": [],
            "case_issues": []
        }
        
        vectors_df = self.load_file("vectors_csv")
        if vectors_df is None:
            result["valid"] = False
            return result
        
        # Get actual skill columns
        all_cols = vectors_df.columns.tolist()
        skill_cols = [c for c in all_cols if c.lower().startswith("skill_")]
        
        # Generate expected columns
        expected_cols = [f"skill_sk{i:03d}" for i in range(1, self.config.expected_skill_count + 1)]
        # Handle 4-digit IDs
        if self.config.expected_skill_count > 999:
            expected_cols = [f"skill_sk{i:03d}" for i in range(1, 1000)]
            expected_cols.extend([f"skill_sk{i:04d}" for i in range(1000, self.config.expected_skill_count + 1)])
        
        # Normalize columns for comparison
        def normalize_col(col: str) -> str:
            """Normalize column name: skill_sk001 or skill_SK001 -> skill_sk001"""
            match = re.match(r"skill_[sS][kK]0*(\d+)", col)
            if match:
                num = int(match.group(1))
                if num < 1000:
                    return f"skill_sk{num:03d}"
                else:
                    return f"skill_sk{num:04d}"
            return col.lower()
        
        # Check case issues
        for col in skill_cols:
            if col != col.lower():
                result["case_issues"].append(col)
        
        if result["case_issues"]:
            self.tracker.warning(
                "vector_alignment", "job_skill_vectors_v2.csv",
                f"Found {len(result['case_issues'])} columns with uppercase characters",
                f"Examples: {result['case_issues'][:3]}"
            )
        
        # Normalize actual columns
        actual_normalized = {normalize_col(c) for c in skill_cols}
        expected_normalized = set(expected_cols)
        
        # Find missing columns
        result["missing_columns"] = sorted(expected_normalized - actual_normalized)
        if result["missing_columns"]:
            self.tracker.critical(
                "vector_alignment", "job_skill_vectors_v2.csv",
                f"Missing {len(result['missing_columns'])} skill columns",
                f"First few: {result['missing_columns'][:5]}"
            )
            result["valid"] = False
        
        # Find extra columns
        result["extra_columns"] = sorted(actual_normalized - expected_normalized)
        if result["extra_columns"]:
            self.tracker.warning(
                "vector_alignment", "job_skill_vectors_v2.csv",
                f"Found {len(result['extra_columns'])} unexpected skill columns",
                f"Examples: {result['extra_columns'][:5]}"
            )
        
        # Check column order
        actual_order = [normalize_col(c) for c in skill_cols]
        expected_order = sorted(expected_cols, key=lambda x: int(re.search(r'\d+', x).group()))
        
        # Only compare columns that exist in both
        common_cols = actual_normalized & expected_normalized
        actual_common = [c for c in actual_order if c in common_cols]
        expected_common = [c for c in expected_order if c in common_cols]
        
        if actual_common != expected_common:
            # Find first mismatch
            for i, (a, e) in enumerate(zip(actual_common, expected_common)):
                if a != e:
                    result["wrong_order"].append((i, a, e))
                    break
            
            if result["wrong_order"]:
                self.tracker.warning(
                    "vector_alignment", "job_skill_vectors_v2.csv",
                    "Skill columns are not in sorted order",
                    f"First mismatch at position {result['wrong_order'][0][0]}: got {result['wrong_order'][0][1]}, expected {result['wrong_order'][0][2]}"
                )
        
        if result["valid"]:
            self.logger.info("  ✓ Vector columns are properly aligned")
        else:
            self.logger.error("  ✗ Vector column alignment issues found")
        
        return result
    
    def check_job_skill_mapping(self) -> Dict[str, Any]:
        """
        Check that each job's matched_skill_ids exist in skills_v2.csv:
        - Flag orphan skills (referenced but not in master list)
        - Validate skill ID format in mappings
        """
        result = {
            "valid": True,
            "orphan_skills": set(),
            "invalid_format": [],
            "jobs_with_issues": []
        }
        
        skills_df = self.load_file("skills_csv")
        jobs_df = self.load_file("jobs_csv")
        
        if skills_df is None or jobs_df is None:
            result["valid"] = False
            return result
        
        # Get valid skill IDs from master list
        valid_skill_ids = set(
            skills_df["skill_id"].astype(str).str.upper().str.strip()
        )
        
        # Check if jobs have matched_skill_ids column
        if "matched_skill_ids" not in jobs_df.columns:
            self.tracker.critical(
                "job_skill_mapping", "jobs_tagged_v2.csv",
                "Missing 'matched_skill_ids' column"
            )
            result["valid"] = False
            return result
        
        # Check each job's skill mappings
        id_pattern = re.compile(r"^SK\d{3,4}$")
        
        for idx, row in jobs_df.iterrows():
            job_uid = row.get("job_uid", f"row_{idx}")
            skill_ids_str = row.get("matched_skill_ids", "")
            
            if pd.isna(skill_ids_str) or not skill_ids_str:
                continue
            
            # Parse skill IDs (semicolon-separated)
            skill_ids = [s.strip().upper() for s in str(skill_ids_str).split(";") if s.strip()]
            
            job_issues = []
            for skill_id in skill_ids:
                # Check format
                if not id_pattern.match(skill_id):
                    result["invalid_format"].append((job_uid, skill_id))
                    job_issues.append(f"Invalid format: {skill_id}")
                
                # Check if exists in master
                if skill_id not in valid_skill_ids:
                    result["orphan_skills"].add(skill_id)
                    job_issues.append(f"Orphan skill: {skill_id}")
            
            if job_issues:
                result["jobs_with_issues"].append((job_uid, job_issues))
        
        # Report findings
        if result["orphan_skills"]:
            self.tracker.critical(
                "job_skill_mapping", "jobs_tagged_v2.csv",
                f"Found {len(result['orphan_skills'])} orphan skill IDs not in master list",
                f"Examples: {list(result['orphan_skills'])[:5]}"
            )
            result["valid"] = False
        
        if result["invalid_format"]:
            self.tracker.warning(
                "job_skill_mapping", "jobs_tagged_v2.csv",
                f"Found {len(result['invalid_format'])} skill IDs with invalid format"
            )
        
        if result["valid"]:
            self.logger.info(f"  ✓ All job skill mappings are valid ({len(jobs_df)} jobs checked)")
        else:
            self.logger.error(f"  ✗ Job skill mapping issues found in {len(result['jobs_with_issues'])} jobs")
        
        return result
    
    def check_model_compatibility(self) -> Dict[str, Any]:
        """
        Check that model column names match vector columns exactly.
        """
        result = {
            "valid": True,
            "mismatched_columns": [],
            "missing_in_model": [],
            "missing_in_vectors": []
        }
        
        if not HAS_JOBLIB:
            self.logger.warning("  ! Skipping model check - joblib not available")
            return result
        
        model_cols = self.load_file("columns_pkl")
        vectors_df = self.load_file("vectors_csv")
        
        if model_cols is None or vectors_df is None:
            result["valid"] = False
            return result
        
        # Get vector skill columns
        vector_skill_cols = sorted([c for c in vectors_df.columns if c.startswith("skill_")])
        model_skill_cols = sorted(model_cols)
        
        # Compare sets
        vector_set = set(vector_skill_cols)
        model_set = set(model_skill_cols)
        
        result["missing_in_model"] = sorted(vector_set - model_set)
        result["missing_in_vectors"] = sorted(model_set - vector_set)
        
        if result["missing_in_model"]:
            self.tracker.critical(
                "model_compatibility", "skill_columns_v2.pkl",
                f"Model missing {len(result['missing_in_model'])} columns present in vectors",
                f"Examples: {result['missing_in_model'][:5]}"
            )
            result["valid"] = False
        
        if result["missing_in_vectors"]:
            self.tracker.critical(
                "model_compatibility", "job_skill_vectors_v2.csv",
                f"Vectors missing {len(result['missing_in_vectors'])} columns present in model",
                f"Examples: {result['missing_in_vectors'][:5]}"
            )
            result["valid"] = False
        
        # Check order matches
        if vector_skill_cols != model_skill_cols:
            # Find first difference
            for i, (v, m) in enumerate(zip(vector_skill_cols, model_skill_cols)):
                if v != m:
                    result["mismatched_columns"].append((i, v, m))
                    break
            
            if result["mismatched_columns"]:
                self.tracker.warning(
                    "model_compatibility", "skill_columns_v2.pkl",
                    "Column order differs between model and vectors",
                    f"First mismatch at index {result['mismatched_columns'][0][0]}"
                )
        
        if result["valid"]:
            self.logger.info("  ✓ Model columns match vector columns")
        else:
            self.logger.error("  ✗ Model compatibility issues found")
        
        return result


# =============================================================================
# AUTO-FIX FUNCTIONS
# =============================================================================

class DataFixer:
    """Applies fixes to resolve data alignment issues."""
    
    def __init__(self, config: PipelineConfig, tracker: IssueTracker,
                 logger: logging.Logger, dry_run: bool = False):
        self.config = config
        self.tracker = tracker
        self.logger = logger
        self.dry_run = dry_run
        self.fixes_applied: List[str] = []
    
    def create_backup(self, files: List[str] = None) -> bool:
        """Create backups of all data files before making changes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.config.root_dir / self.config.backup_dir / timestamp
        
        if files is None:
            files = [
                "skills_csv", "jobs_csv", "vectors_csv", 
                "profiles_csv", "ladders_json", "columns_pkl"
            ]
        
        self.logger.info(f"\nCreating backups in: {backup_dir}")
        
        if self.dry_run:
            self.logger.info("  [DRY RUN] Would create backup directory")
            return True
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for file_key in files:
                src = self.config.get_path(file_key)
                if src.exists():
                    dst = backup_dir / src.name
                    shutil.copy2(src, dst)
                    self.logger.info(f"  ✓ Backed up: {src.name}")
                else:
                    self.logger.warning(f"  ! File not found: {src.name}")
            
            self.logger.info(f"  Backup complete: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"  ✗ Backup failed: {e}")
            return False
    
    def fix_skill_ids(self, skills_df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize skill IDs to SK### format (uppercase, zero-padded).
        
        Fixes:
        - sk001 -> SK001
        - SK1 -> SK001
        - " SK001 " -> SK001
        """
        self.logger.info("\n[FIX] Standardizing Skill IDs...")
        
        if "skill_id" not in skills_df.columns:
            self.logger.error("  ✗ No skill_id column found")
            return skills_df
        
        original_ids = skills_df["skill_id"].tolist()
        fixed_ids = []
        changes = 0
        
        id_pattern = re.compile(r"[sS][kK]0*(\d+)")
        
        for sid in original_ids:
            sid_str = str(sid).strip()
            match = id_pattern.search(sid_str)
            
            if match:
                num = int(match.group(1))
                # Use 3-digit padding for <1000, 4-digit for >=1000
                if num < 1000:
                    new_id = f"SK{num:03d}"
                else:
                    new_id = f"SK{num:04d}"
                
                if new_id != sid:
                    changes += 1
                fixed_ids.append(new_id)
            else:
                self.logger.warning(f"  ! Could not parse skill ID: {sid}")
                fixed_ids.append(sid_str.upper())
        
        if self.dry_run:
            self.logger.info(f"  [DRY RUN] Would fix {changes} skill IDs")
        else:
            skills_df["skill_id"] = fixed_ids
            self.logger.info(f"  ✓ Fixed {changes} skill IDs")
            self.fixes_applied.append(f"Standardized {changes} skill IDs")
            self.tracker.stats["fixes_applied"] += 1
        
        return skills_df
    
    def rebuild_vectors(self, jobs_df: pd.DataFrame, skills_df: pd.DataFrame) -> pd.DataFrame:
        """
        Rebuild the job-skill vector matrix from scratch.
        
        Creates a perfect N_jobs × N_skills binary matrix where:
        - Rows = jobs (by job_uid)
        - Columns = skill_sk001, skill_sk002, ..., skill_sk1147
        - Values = 1 if job has skill, 0 otherwise
        """
        self.logger.info("\n[FIX] Rebuilding Job-Skill Vectors...")
        
        # Create skill ID to column name mapping
        n_skills = len(skills_df)
        skill_id_to_col = {}
        for i, row in skills_df.iterrows():
            sid = str(row["skill_id"]).strip().upper()
            # Normalize to SK### format
            match = re.match(r"SK0*(\d+)", sid)
            if match:
                num = int(match.group(1))
                col_name = f"skill_sk{num:03d}" if num < 1000 else f"skill_sk{num:04d}"
                skill_id_to_col[sid] = col_name
        
        # Generate sorted column names
        skill_columns = sorted(skill_id_to_col.values(), 
                               key=lambda x: int(re.search(r'\d+', x).group()))
        
        self.logger.info(f"  Building {len(jobs_df)} x {len(skill_columns)} matrix...")
        
        if self.dry_run:
            self.logger.info(f"  [DRY RUN] Would rebuild vectors matrix")
            return None
        
        # Initialize matrix
        matrix = np.zeros((len(jobs_df), len(skill_columns)), dtype=np.int8)
        col_to_idx = {col: i for i, col in enumerate(skill_columns)}
        
        # Populate matrix
        id_pattern = re.compile(r"SK0*(\d+)", re.IGNORECASE)
        
        for job_idx, row in jobs_df.iterrows():
            skill_ids_str = row.get("matched_skill_ids", "")
            if pd.isna(skill_ids_str) or not skill_ids_str:
                continue
            
            skill_ids = [s.strip().upper() for s in str(skill_ids_str).split(";") if s.strip()]
            
            for sid in skill_ids:
                # Normalize skill ID
                match = id_pattern.match(sid)
                if match:
                    num = int(match.group(1))
                    col_name = f"skill_sk{num:03d}" if num < 1000 else f"skill_sk{num:04d}"
                    if col_name in col_to_idx:
                        matrix[job_idx, col_to_idx[col_name]] = 1
        
        # Create DataFrame with metadata columns
        meta_cols = ["job_uid", "job_title", "job_title_clean", "role_id", 
                     "role_title", "job_category", "seniority_level"]
        
        available_meta = [c for c in meta_cols if c in jobs_df.columns]
        
        vectors_df = jobs_df[available_meta].copy()
        
        # Add skill columns
        skill_df = pd.DataFrame(matrix, columns=skill_columns, index=jobs_df.index)
        vectors_df = pd.concat([vectors_df, skill_df], axis=1)
        
        self.logger.info(f"  ✓ Rebuilt vectors: {vectors_df.shape[0]} jobs × {len(skill_columns)} skills")
        self.fixes_applied.append(f"Rebuilt vector matrix {vectors_df.shape}")
        self.tracker.stats["fixes_applied"] += 1
        
        return vectors_df
    
    def fix_role_profiles(self, profiles_df: pd.DataFrame, 
                          valid_skill_ids: Set[str],
                          valid_role_ids: Set[str]) -> pd.DataFrame:
        """
        Fix role skill profiles:
        - Remove invalid skill references
        - Standardize skill IDs
        - Remove orphan roles
        """
        self.logger.info("\n[FIX] Fixing Role Skill Profiles...")
        
        if profiles_df is None or profiles_df.empty:
            self.logger.warning("  ! No profiles to fix")
            return profiles_df
        
        original_len = len(profiles_df)
        
        # Standardize skill IDs
        id_pattern = re.compile(r"[sS][kK]0*(\d+)")
        
        def normalize_skill_id(sid):
            if pd.isna(sid):
                return None
            match = id_pattern.search(str(sid))
            if match:
                num = int(match.group(1))
                return f"SK{num:03d}" if num < 1000 else f"SK{num:04d}"
            return None
        
        profiles_df["skill_id_normalized"] = profiles_df["skill_id"].apply(normalize_skill_id)
        
        # Filter out invalid skill IDs
        valid_mask = profiles_df["skill_id_normalized"].isin(valid_skill_ids)
        invalid_skills = (~valid_mask).sum()
        
        # Filter out invalid role IDs if we have valid roles
        if valid_role_ids and "role_id" in profiles_df.columns:
            role_mask = profiles_df["role_id"].isin(valid_role_ids)
            invalid_roles = (~role_mask).sum()
        else:
            role_mask = pd.Series([True] * len(profiles_df))
            invalid_roles = 0
        
        combined_mask = valid_mask & role_mask
        
        if self.dry_run:
            self.logger.info(f"  [DRY RUN] Would remove {invalid_skills} invalid skills, {invalid_roles} invalid roles")
            return profiles_df
        
        cleaned_df = profiles_df[combined_mask].copy()
        cleaned_df["skill_id"] = cleaned_df["skill_id_normalized"]
        cleaned_df = cleaned_df.drop(columns=["skill_id_normalized"])
        
        removed = original_len - len(cleaned_df)
        self.logger.info(f"  ✓ Removed {removed} invalid entries ({invalid_skills} invalid skills, {invalid_roles} invalid roles)")
        self.fixes_applied.append(f"Cleaned {removed} invalid profile entries")
        self.tracker.stats["fixes_applied"] += 1
        
        return cleaned_df
    
    def update_model_columns(self, skill_columns: List[str]) -> List[str]:
        """
        Update skill_columns_v2.pkl to match current vector columns.
        """
        self.logger.info("\n[FIX] Updating Model Columns...")
        
        # Sort columns properly
        sorted_columns = sorted(
            skill_columns,
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
        )
        
        if self.dry_run:
            self.logger.info(f"  [DRY RUN] Would update model columns ({len(sorted_columns)} columns)")
            return sorted_columns
        
        columns_path = self.config.get_path("columns_pkl")
        
        if HAS_JOBLIB:
            joblib.dump(sorted_columns, columns_path)
            self.logger.info(f"  ✓ Updated skill_columns_v2.pkl with {len(sorted_columns)} columns")
            self.fixes_applied.append(f"Updated model columns ({len(sorted_columns)} cols)")
            self.tracker.stats["fixes_applied"] += 1
        else:
            self.logger.error("  ✗ Cannot update model columns - joblib not available")
        
        return sorted_columns
    
    def save_files(self, skills_df: pd.DataFrame = None, 
                   vectors_df: pd.DataFrame = None,
                   profiles_df: pd.DataFrame = None):
        """Save modified DataFrames to files."""
        self.logger.info("\n[SAVE] Writing fixed files...")
        
        if self.dry_run:
            self.logger.info("  [DRY RUN] Would save files")
            return
        
        try:
            if skills_df is not None:
                path = self.config.get_path("skills_csv")
                skills_df.to_csv(path, index=False)
                self.logger.info(f"  ✓ Saved: {path.name}")
            
            if vectors_df is not None:
                path = self.config.get_path("vectors_csv")
                vectors_df.to_csv(path, index=False)
                self.logger.info(f"  ✓ Saved: {path.name}")
            
            if profiles_df is not None:
                path = self.config.get_path("profiles_csv")
                profiles_df.to_csv(path, index=False)
                self.logger.info(f"  ✓ Saved: {path.name}")
                
        except Exception as e:
            self.logger.error(f"  ✗ Error saving files: {e}")
            raise


# =============================================================================
# MAIN PIPELINE
# =============================================================================

class AutofixPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, root_dir: Path = None, dry_run: bool = False,
                 validate_only: bool = False, backup_only: bool = False):
        self.config = PipelineConfig()
        if root_dir:
            self.config.root_dir = Path(root_dir)
        
        self.tracker = IssueTracker()
        self.logger = setup_logging(self.config)
        self.diagnostics = DataDiagnostics(self.config, self.tracker, self.logger)
        self.fixer = DataFixer(self.config, self.tracker, self.logger, dry_run)
        
        self.dry_run = dry_run
        self.validate_only = validate_only
        self.backup_only = backup_only
    
    def run(self) -> int:
        """Run the complete pipeline."""
        start_time = datetime.now()
        
        self.logger.info("=" * 70)
        self.logger.info("AUTOFIX DATA PIPELINE - Career Recommendation System")
        self.logger.info("=" * 70)
        self.logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Root Directory: {self.config.root_dir}")
        self.logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'VALIDATE ONLY' if self.validate_only else 'BACKUP ONLY' if self.backup_only else 'FULL FIX'}")
        self.logger.info("")
        
        # Step 1: Create backups
        if not self.validate_only:
            if not self.fixer.create_backup():
                self.logger.error("Backup failed - aborting")
                return 1
        
        if self.backup_only:
            self.logger.info("\nBackup complete. Exiting (--backup-only mode)")
            return 0
        
        # Step 2: Run diagnostics
        results = self.diagnostics.run_all_diagnostics()
        
        # Step 3: Print diagnostic report
        self._print_diagnostic_report(results)
        
        if self.validate_only:
            self.logger.info("\nValidation complete. Exiting (--validate-only mode)")
            return 1 if self.tracker.has_critical() else 0
        
        # Step 4: Apply fixes if needed
        if self.tracker.get_fixable():
            self._apply_fixes(results)
        else:
            self.logger.info("\nNo fixable issues found!")
        
        # Step 5: Re-validate
        if not self.dry_run and self.fixer.fixes_applied:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("POST-FIX VALIDATION")
            self.logger.info("=" * 60)
            
            # Clear cache and re-run diagnostics
            self.diagnostics.data_cache.clear()
            post_results = self.diagnostics.run_all_diagnostics()
            self._print_validation_summary(post_results)
        
        # Step 6: Final summary
        elapsed = datetime.now() - start_time
        self._print_final_summary(elapsed)
        
        return 0 if not self.tracker.has_critical() else 1
    
    def _print_diagnostic_report(self, results: Dict[str, Any]):
        """Print detailed diagnostic report."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("DIAGNOSTIC REPORT")
        self.logger.info("=" * 60)
        
        # Skill IDs
        skill_result = results.get("skill_ids", {})
        if skill_result.get("invalid_ids"):
            self.logger.info(f"\nInvalid Skill IDs: {len(skill_result['invalid_ids'])}")
            for idx, sid in skill_result["invalid_ids"][:5]:
                self.logger.info(f"  - Row {idx}: '{sid}'")
        
        if skill_result.get("duplicates"):
            self.logger.info(f"\nDuplicate Skill IDs: {len(skill_result['duplicates'])}")
            for idx, sid in skill_result["duplicates"][:5]:
                self.logger.info(f"  - Row {idx}: '{sid}'")
        
        if skill_result.get("gaps"):
            self.logger.info(f"\nGaps in Skill ID Sequence: {len(skill_result['gaps'])}")
            self.logger.info(f"  First few: {skill_result['gaps'][:10]}")
        
        # Skill Counts
        count_result = results.get("skill_counts", {})
        if count_result.get("mismatches"):
            self.logger.info(f"\nSkill Count Mismatches:")
            for source, actual, expected in count_result["mismatches"]:
                self.logger.info(f"  - {source}: {actual} (expected {expected})")
        
        # Vector Alignment
        vector_result = results.get("vector_alignment", {})
        if vector_result.get("missing_columns"):
            self.logger.info(f"\nMissing Vector Columns: {len(vector_result['missing_columns'])}")
        if vector_result.get("extra_columns"):
            self.logger.info(f"Extra Vector Columns: {len(vector_result['extra_columns'])}")
        
        # Job-Skill Mapping
        mapping_result = results.get("job_skill_mapping", {})
        if mapping_result.get("orphan_skills"):
            self.logger.info(f"\nOrphan Skills (in jobs but not master): {len(mapping_result['orphan_skills'])}")
            orphans = list(mapping_result["orphan_skills"])[:10]
            self.logger.info(f"  Examples: {orphans}")
        
        # Model Compatibility
        model_result = results.get("model_compatibility", {})
        if model_result.get("missing_in_model"):
            self.logger.info(f"\nColumns missing in model: {len(model_result['missing_in_model'])}")
        if model_result.get("missing_in_vectors"):
            self.logger.info(f"Columns missing in vectors: {len(model_result['missing_in_vectors'])}")
        
        # Issue summary
        self.logger.info("\n" + self.tracker.summary())
    
    def _apply_fixes(self, results: Dict[str, Any]):
        """Apply necessary fixes based on diagnostic results."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("APPLYING FIXES")
        self.logger.info("=" * 60)
        
        # Load current data
        skills_df = self.diagnostics.load_file("skills_csv")
        jobs_df = self.diagnostics.load_file("jobs_csv")
        profiles_df = self.diagnostics.load_file("profiles_csv")
        
        modified_skills = False
        modified_vectors = False
        modified_profiles = False
        
        # Fix 1: Standardize skill IDs
        skill_result = results.get("skill_ids", {})
        if (skill_result.get("case_issues") or 
            skill_result.get("whitespace_issues") or 
            skill_result.get("invalid_ids")):
            skills_df = self.fixer.fix_skill_ids(skills_df)
            modified_skills = True
        
        # Fix 2: Rebuild vectors if needed
        vector_result = results.get("vector_alignment", {})
        count_result = results.get("skill_counts", {})
        
        needs_vector_rebuild = (
            vector_result.get("missing_columns") or
            vector_result.get("wrong_order") or
            count_result.get("mismatches")
        )
        
        if needs_vector_rebuild and skills_df is not None and jobs_df is not None:
            vectors_df = self.fixer.rebuild_vectors(jobs_df, skills_df)
            modified_vectors = True
        else:
            vectors_df = None
        
        # Fix 3: Fix role profiles
        if profiles_df is not None:
            valid_skill_ids = set(skills_df["skill_id"].astype(str).str.upper().str.strip())
            
            # Get valid role IDs from ladders
            ladders = self.diagnostics.load_file("ladders_json")
            valid_role_ids = set()
            if ladders:
                for track_roles in ladders.values():
                    valid_role_ids.update(track_roles)
            
            mapping_result = results.get("job_skill_mapping", {})
            if mapping_result.get("orphan_skills") or mapping_result.get("invalid_format"):
                profiles_df = self.fixer.fix_role_profiles(
                    profiles_df, valid_skill_ids, valid_role_ids
                )
                modified_profiles = True
        
        # Fix 4: Update model columns
        model_result = results.get("model_compatibility", {})
        if (model_result.get("missing_in_model") or 
            model_result.get("missing_in_vectors") or
            model_result.get("mismatched_columns")):
            
            # Get correct column list
            if vectors_df is not None:
                skill_cols = [c for c in vectors_df.columns if c.startswith("skill_")]
            else:
                vectors_loaded = self.diagnostics.load_file("vectors_csv")
                if vectors_loaded is not None:
                    skill_cols = [c for c in vectors_loaded.columns if c.startswith("skill_")]
                else:
                    skill_cols = [f"skill_sk{i:03d}" for i in range(1, self.config.expected_skill_count + 1)]
            
            self.fixer.update_model_columns(skill_cols)
        
        # Save modified files
        self.fixer.save_files(
            skills_df=skills_df if modified_skills else None,
            vectors_df=vectors_df if modified_vectors else None,
            profiles_df=profiles_df if modified_profiles else None
        )
    
    def _print_validation_summary(self, results: Dict[str, Any]):
        """Print summary of post-fix validation."""
        all_valid = all(r.get("valid", True) for r in results.values() if isinstance(r, dict))
        
        if all_valid:
            self.logger.info("\n✓ All validation checks passed!")
        else:
            self.logger.warning("\n✗ Some issues remain after fixes:")
            for name, result in results.items():
                if isinstance(result, dict) and not result.get("valid", True):
                    self.logger.warning(f"  - {name}")
    
    def _print_final_summary(self, elapsed):
        """Print final summary."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("FINAL SUMMARY")
        self.logger.info("=" * 70)
        
        self.logger.info(f"\nTime Elapsed: {elapsed}")
        self.logger.info(f"Files Scanned: {self.tracker.stats['files_scanned']}")
        self.logger.info(f"Issues Found: {len(self.tracker.issues)}")
        self.logger.info(f"  - CRITICAL: {self.tracker.stats['CRITICAL']}")
        self.logger.info(f"  - WARNING: {self.tracker.stats['WARNING']}")
        self.logger.info(f"Fixes Applied: {self.tracker.stats['fixes_applied']}")
        
        if self.fixer.fixes_applied:
            self.logger.info("\nFixes Applied:")
            for fix in self.fixer.fixes_applied:
                self.logger.info(f"  ✓ {fix}")
        
        # Exit status
        if self.tracker.has_critical():
            self.logger.error("\n✗ PIPELINE COMPLETED WITH ERRORS")
            self.logger.info("  Review the issues above and re-run if needed.")
        else:
            self.logger.info("\n✓ PIPELINE COMPLETED SUCCESSFULLY")
        
        self.logger.info("\nLog file: autofix_pipeline.log")
        self.logger.info("=" * 70)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autofix Data Pipeline - Diagnose and fix Career ML data alignment issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autofix_data_pipeline.py                    # Run full diagnostics and fixes
  python autofix_data_pipeline.py --dry-run          # Show what would be fixed
  python autofix_data_pipeline.py --validate-only    # Run diagnostics only
  python autofix_data_pipeline.py --backup-only      # Create backups only

Exit Codes:
  0 - Success (no critical issues)
  1 - Failed (critical issues remain)
        """
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be fixed without making changes"
    )
    
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Run diagnostics only, don't apply fixes"
    )
    
    parser.add_argument(
        "--backup-only", "-b",
        action="store_true",
        help="Create backups only, then exit"
    )
    
    parser.add_argument(
        "--root-dir", "-r",
        type=str,
        default=None,
        help="Root directory for career-ml data (default: script location)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    pipeline = AutofixPipeline(
        root_dir=args.root_dir,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
        backup_only=args.backup_only
    )
    
    exit_code = pipeline.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
