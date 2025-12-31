# tests/test_repository.py
from app.repositories.program_repository import ProgramRepository


def test_program_repository_loads_data():
    repo = ProgramRepository()
    programs = repo.get_all_programs()

    assert programs is not None
    assert len(programs) > 0

    program = programs[0]
    assert program.program_id
    assert program.degree_name
