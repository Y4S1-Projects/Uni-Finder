# app/api/courses.py
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.repositories.cutoff_repository import CutoffRepository
from app.repositories.program_repository import ProgramRepository

router = APIRouter()
program_repo = ProgramRepository()
cutoff_repo = CutoffRepository()


class EmptyRequest(BaseModel):
    pass


class CourseCodeRequest(BaseModel):
    course_code: str = Field(..., min_length=1)


class CourseCutoffRequest(BaseModel):
    course_code: str = Field(..., min_length=1)
    district: Optional[str] = None


class StreamRequest(BaseModel):
    stream: str = Field(..., min_length=1)


class CourseSearchRequest(BaseModel):
    q: str = Field(..., min_length=1, description="Search query")
    stream: Optional[str] = None
    university: Optional[str] = None


def _normalize_course_code(course_code: str) -> str:
    code = str(course_code).strip()
    try:
        return f"{int(code):03d}"
    except ValueError:
        return code


@router.post("/courses")
def get_all_courses(_: EmptyRequest):
    """
    Get all available degree courses from University_Courses_Dataset.csv.
    Request parameters are passed in JSON body.
    """
    programs = program_repo.get_all_programs()
    return {
        "total_count": len(programs),
        "courses": [program.to_dict() for program in programs],
    }


@router.post("/courses/by-code")
def get_course_by_code(request: CourseCodeRequest):
    """
    Get detailed information about a specific course by its course code.
    Request parameters are passed in JSON body.
    """
    course_code = _normalize_course_code(request.course_code)
    program = program_repo.get_program_by_code(course_code)

    if not program:
        raise HTTPException(status_code=404, detail=f"Course {course_code} not found")

    return program.to_dict()


@router.post("/courses/cutoffs")
def get_course_cutoffs(request: CourseCutoffRequest):
    """
    Get Z-score cutoffs for a course across all universities.
    Optionally filter by district.
    Request parameters are passed in JSON body.
    """
    course_code = _normalize_course_code(request.course_code)
    district = request.district

    program = program_repo.get_program_by_code(course_code)
    if not program:
        raise HTTPException(status_code=404, detail=f"Course {course_code} not found")

    all_offerings = cutoff_repo.get_all_cutoffs_for_course(course_code)

    if not all_offerings:
        return {
            "course_code": course_code,
            "course_name": program.course_name,
            "message": "No cutoff data available for this course",
            "offerings": [],
        }

    offerings = []
    for offering in all_offerings:
        university_data = {
            "university": offering["university"],
            "course_name": offering["course_name"],
        }

        if district:
            zscore = offering["cutoffs_by_district"].get(district)
            university_data["district"] = district
            university_data["cutoff_zscore"] = zscore
        else:
            university_data["cutoffs_by_district"] = offering["cutoffs_by_district"]

        offerings.append(university_data)

    return {
        "course_code": course_code,
        "course_name": program.course_name,
        "offerings": offerings,
    }


@router.post("/courses/by-stream")
def get_courses_by_stream(request: StreamRequest):
    """
    Get all courses for a specific stream (e.g., Science, Arts, Commerce).
    Request parameters are passed in JSON body.
    """
    programs = program_repo.get_programs_by_stream(request.stream)
    return {
        "stream": request.stream,
        "total_count": len(programs),
        "courses": [program.to_dict() for program in programs],
    }


@router.post("/districts")
def get_districts(_: EmptyRequest):
    """
    Get list of all districts for which cutoff data is available.
    Request parameters are passed in JSON body.
    """
    cutoff_repo.load()
    return {
        "districts": cutoff_repo.districts,
        "total_count": len(cutoff_repo.districts),
    }


@router.post("/streams")
def get_streams(_: EmptyRequest):
    """
    Get list of all available streams from the course catalog.
    Request parameters are passed in JSON body.
    """
    programs = program_repo.get_all_programs()
    streams = set()
    for program in programs:
        if program.stream:
            streams.add(program.stream)

    streams_list = sorted(list(streams))
    return {"streams": streams_list, "total_count": len(streams_list)}


@router.post("/universities")
def get_universities(_: EmptyRequest):
    """
    Get list of all universities offering degree programs.
    Request parameters are passed in JSON body.
    """
    programs = program_repo.get_all_programs()
    universities = set()
    for program in programs:
        for university in program.universities:
            if university:
                universities.add(university)

    universities_list = sorted(list(universities))
    return {"universities": universities_list, "total_count": len(universities_list)}


@router.post("/search")
def search_courses(request: CourseSearchRequest):
    """
    Search courses by name, keywords, or other criteria.
    Request parameters are passed in JSON body.
    """
    programs = program_repo.get_all_programs()

    if request.stream:
        programs = [
            p
            for p in programs
            if p.stream and request.stream.lower() in p.stream.lower()
        ]

    if request.university:
        programs = [
            p
            for p in programs
            if any(request.university.lower() in uni.lower() for uni in p.universities)
        ]

    q_lower = request.q.lower()
    matching_programs = []

    for program in programs:
        if (
            q_lower in program.course_name.lower()
            or q_lower in program.notes.lower()
            or q_lower in program.faculty_department.lower()
            or q_lower in program.degree_programme.lower()
        ):
            matching_programs.append(program)

    return {
        "query": request.q,
        "filters": {"stream": request.stream, "university": request.university},
        "total_count": len(matching_programs),
        "courses": [program.to_dict() for program in matching_programs],
    }
