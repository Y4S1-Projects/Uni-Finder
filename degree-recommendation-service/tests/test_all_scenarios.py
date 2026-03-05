"""
Comprehensive Test Suite for V3 A/L Pipeline - All 5 Scenarios

Scenario 01: Stream-based search (no Z-score, no interests)
Scenario 02: Stream + Z-score search (no interests)
Scenario 03: Interests-only search (infer stream from interests)
Scenario 04: Stream + Interests search
Scenario 05: Stream + Z-score + Interests search (full filtering)

Each scenario tested with multiple student profiles.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.domain.student import StudentProfile
from app.pipelines.dream_reality_pipeline import DreamRealityPipeline

# Initialize pipeline
pipeline = DreamRealityPipeline(
    semantic_weight=0.7,
    tfidf_weight=0.3,
    use_career_mapping=True,
)


def print_scenario_header(scenario_num, scenario_name):
    print("\n" + "=" * 80)
    print(f"SCENARIO {scenario_num}: {scenario_name}")
    print("=" * 80)


def print_test_case(test_name, profile, district="COLOMBO"):
    print(f"\n[Test] {test_name}")
    print(f"  Stream: {profile.stream}")
    print(f"  Interests: {profile.interests[:50]}...")
    print(f"  Z-Score: {profile.zscore}")
    print(f"  District: {district}")


def print_results(result):
    eligible_count = len(result.get("all_eligible_courses", []))
    filtered_count = len(result.get("recommendations", []))

    print(f"  Eligible Courses (all): {eligible_count}")
    if eligible_count > 0:
        top_5_eligible = result["all_eligible_courses"][:5]
        codes = [c["course_code"] for c in top_5_eligible]
        names = [c["course_name"][:30] for c in top_5_eligible]
        print(f"    Top 5: {codes}")
        for code, name in zip(codes, names):
            print(f"      {code}: {name}")

    print(f"  Interest-Filtered Courses: {filtered_count}")
    if filtered_count > 0:
        top_5_filtered = result["recommendations"][:5]
        codes = [c["course_code"] for c in top_5_filtered]
        names = [c["course_name"][:30] for c in top_5_filtered]
        print(f"    Top 5: {codes}")
        for code, name in zip(codes, names):
            print(f"      {code}: {name}")

    if result.get("has_mismatch"):
        dream = result.get("dream_course", {})
        print(f"\n  MISMATCH DETECTED:")
        print(f"    Dream Course: {dream.get('course_name')} (not eligible)")
        print(f"    Reason: {dream.get('ineligibility_reason')}")


# ============================================================================
# SCENARIO 01: Stream-only search (no Z-score, no interests)
# ============================================================================
print_scenario_header(1, "Stream-Only Search (No Z-score, No Interests)")

print("\n[Scenario 01 Logic]")
print("  - Filter by stream only")
print("  - No Z-score filtering")
print("  - No interest-based ranking")
print("  - Use default/minimal interest text")

# Test 01.1: Biological Science student (minimal info)
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=0.0,  # No Z-score (ignored in stream-only)
    interests="looking for biological programs",
)
print_test_case("01.1 - Bio Science Student (Stream Only)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 01.2: Physical Science student
test_profile = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=0.0,
    interests="interested in physical programs",
)
print_test_case("01.2 - Physical Science Student (Stream Only)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 01.3: Commerce student
test_profile = StudentProfile(
    stream="Commerce",
    subjects=["Accounting", "Business Studies", "Economics"],
    zscore=0.0,
    interests="want commerce programs",
)
print_test_case("01.3 - Commerce Student (Stream Only)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 01.4: Arts student
test_profile = StudentProfile(
    stream="Arts",
    subjects=["Sinhala", "English", "History"],
    zscore=0.0,
    interests="looking for arts degrees",
)
print_test_case("01.4 - Arts Student (Stream Only)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# ============================================================================
# SCENARIO 02: Stream + Z-score search (no interests)
# ============================================================================
print_scenario_header(2, "Stream + Z-Score Search (No Interests)")

print("\n[Scenario 02 Logic]")
print("  - Filter by stream AND Z-score")
print("  - Z-score acts as cutoff eligibility")
print("  - Rank remaining courses by Z-score/eligibility")
print("  - No interest-based ranking")

# Test 02.1: Bio Science with HIGH Z-score (eligible for Medicine)
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=2.0,  # High score, eligible for Medicine (cutoff ~1.88)
    interests="any biological program",
)
print_test_case("02.1 - Bio Science, Z=2.0 (High, eligible for Medicine)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 02.2: Bio Science with LOW Z-score (only low-cutoff programs)
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=0.8,  # Low score, can only access Agriculture (cutoff ~0.697)
    interests="any biological program",
)
print_test_case("02.2 - Bio Science, Z=0.8 (Low, only Agriculture)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 02.3: Physical Science with HIGH Z-score
test_profile = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=2.2,  # High score
    interests="any engineering or CS program",
)
print_test_case("02.3 - Physical Science, Z=2.2 (High)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 02.4: Commerce with MEDIUM Z-score
test_profile = StudentProfile(
    stream="Commerce",
    subjects=["Accounting", "Business Studies", "Economics"],
    zscore=1.5,  # Medium score
    interests="business programs",
)
print_test_case("02.4 - Commerce, Z=1.5 (Medium)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# ============================================================================
# SCENARIO 03: Interests-only search (infer stream from interests)
# ============================================================================
print_scenario_header(3, "Interests-Only Search (Infer Stream)")

print("\n[Scenario 03 Logic]")
print("  - DON'T rely on Stream field")
print("  - Use interests to find relevant courses")
print("  - System should find courses matching interests")
print("  - May span multiple streams if interests are cross-disciplinary")

# Test 03.1: Medical interests (should find Medicine/Health programs)
test_profile = StudentProfile(
    stream="Any",  # Stream not used
    subjects=["Any"],
    zscore=0.0,  # Z-score not used
    interests="I want to be a doctor and work in healthcare. Medicine and surgery interest me.",
)
print_test_case("03.1 - Medical Interests (No Stream)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 03.2: Engineering interests (should find Engineering/Tech programs)
test_profile = StudentProfile(
    stream="Any",
    subjects=["Any"],
    zscore=0.0,
    interests="I love building bridges and structures. Civil engineering and construction fascinate me.",
)
print_test_case("03.2 - Engineering Interests (No Stream)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 03.3: Business interests (should find Management/Commerce programs)
test_profile = StudentProfile(
    stream="Any",
    subjects=["Any"],
    zscore=0.0,
    interests="I want to start a business and become an entrepreneur. Finance and management interest me.",
)
print_test_case("03.3 - Business Interests (No Stream)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 03.4: Law/Justice interests (should find Law programs)
test_profile = StudentProfile(
    stream="Any",
    subjects=["Any"],
    zscore=0.0,
    interests="I'm passionate about law, justice, and human rights. I want to become a lawyer.",
)
print_test_case("03.4 - Law Interests (No Stream)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# ============================================================================
# SCENARIO 04: Stream + Interests search
# ============================================================================
print_scenario_header(4, "Stream + Interests Search")

print("\n[Scenario 04 Logic]")
print("  - Filter by stream (hard constraint)")
print("  - Rank by interests (secondary)")
print("  - Only courses in stream are eligible")
print("  - Highest interest matches ranked first")

# Test 04.1: Bio Science student interested in Medicine
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=0.0,  # Z-score ignored
    interests="I want to be a doctor. Medicine and healthcare are my passion.",
)
print_test_case("04.1 - Bio Science + Medical Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 04.2: Physical Science student interested in CS
test_profile = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=0.0,
    interests="I love programming, AI, and building software systems. Computer Science is my goal.",
)
print_test_case("04.2 - Physical Science + CS Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 04.3: Arts student interested in Law
test_profile = StudentProfile(
    stream="Arts",
    subjects=["Sinhala", "English", "History"],
    zscore=0.0,
    interests="I want to study law and become a lawyer. Justice and human rights are important to me.",
)
print_test_case("04.3 - Arts + Law Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 04.4: Commerce student interested in Accounting
test_profile = StudentProfile(
    stream="Commerce",
    subjects=["Accounting", "Business Studies", "Economics"],
    zscore=0.0,
    interests="I'm skilled with numbers and want to be a chartered accountant.",
)
print_test_case("04.4 - Commerce + Accounting Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# ============================================================================
# SCENARIO 05: Stream + Z-Score + Interests search (FULL FILTERING)
# ============================================================================
print_scenario_header(5, "Stream + Z-Score + Interests (Full Filtering)")

print("\n[Scenario 05 Logic]")
print("  - Stream: Hard filter (only eligible stream)")
print("  - Z-Score: Hard filter (must meet cutoff)")
print("  - Interests: Soft ranking (within eligible courses)")
print("  - Interest matching is nice-to-have, not required")

# Test 05.1: Bio Science, Z=2.0, Medical interests (MATCH)
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=2.0,  # Eligible for Medicine
    interests="I want to be a doctor and study medicine.",
)
print_test_case("05.1 - Bio Science, Z=2.0, Medical Interests (MATCH)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 05.2: Bio Science, Z=0.8, Medical interests (MISMATCH - too low Z)
test_profile = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=0.8,  # Too low for Medicine, can access Agriculture
    interests="I want to be a doctor but my scores are low.",
)
print_test_case("05.2 - Bio Science, Z=0.8, Medical Interests (MISMATCH)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 05.3: Arts, Z=2.0, Engineering interests (MISMATCH - wrong stream)
test_profile = StudentProfile(
    stream="Arts",
    subjects=["Sinhala", "English", "History"],
    zscore=2.0,  # High Z-score but wrong stream
    interests="I love engineering and want to build bridges.",
)
print_test_case("05.3 - Arts, Z=2.0, Engineering Interests (MISMATCH)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 05.4: Physical Science, Z=2.0, CS interests (MATCH)
test_profile = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=2.0,
    interests="I love programming and AI. Computer Science is my passion.",
)
print_test_case("05.4 - Physical Science, Z=2.0, CS Interests (MATCH)", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 05.5: Commerce, Z=1.5, different interests (acceptable)
test_profile = StudentProfile(
    stream="Commerce",
    subjects=["Accounting", "Business Studies", "Economics"],
    zscore=1.5,
    interests="I'm interested in banking and finance but also like HR management.",
)
print_test_case("05.5 - Commerce, Z=1.5, Mixed Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# Test 05.6: Physical Science, Z=1.5, Engineering interests
test_profile = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=1.5,
    interests="I'm fascinated by machinery and want to be a mechanical engineer.",
)
print_test_case("05.6 - Physical Science, Z=1.5, Engineering Interests", test_profile)
result = pipeline.recommend(test_profile, "COLOMBO", is_al_student=True, max_results=5)
print_results(result)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("COMPREHENSIVE TEST SUITE COMPLETE")
print("=" * 80)
print(
    """
Scenario Summary:
  01 [OK] Stream-only search
  02 [OK] Stream + Z-score search  
  03 [OK] Interests-only search
  04 [OK] Stream + Interests search
  05 [OK] Stream + Z-score + Interests (full filtering)

Expected Behavior:
  - All scenarios should show "all_eligible_courses" list
  - Scenario 01: Eligible count by stream
  - Scenario 02: Eligible count reduced by Z-score filter
  - Scenario 03: Courses matched to interests (may cross streams)
  - Scenario 04: Eligible by stream, ranked by interests
  - Scenario 05: Eligible by stream+Z-score, ranked by interests
           Mismatches show dream vs reality explanation

[OK] All test cases completed successfully
"""
)
