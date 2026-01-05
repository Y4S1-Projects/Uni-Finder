"""Skill-related utilities"""
from data_loader import DataStore


def get_skill_name(skill_id: str) -> str:
    """Get human-readable skill name from skill ID"""
    return DataStore.skill_id_to_name.get(skill_id.upper(), skill_id)


def resolve_skill_names(skill_ids: list) -> list:
    """Convert list of skill IDs to human-readable names"""
    return [get_skill_name(sid) for sid in skill_ids]
