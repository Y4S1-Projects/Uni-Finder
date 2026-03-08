"""
Regenerate career_ladders_enhanced.json using correct role-to-domain mapping.

This script:
1. Uses career_ladders_v2.json for correct role → domain mapping
2. Only includes roles that have data in job_skill_vectors.csv
3. Enhances each level with skills, job counts, salary ranges etc.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any


def load_data(base_dir: Path):
    """Load all required data files."""
    # Career ladders with correct role-to-domain mapping
    with open(base_dir / 'data/processed/career_ladders_v2.json', 'r') as f:
        career_ladders = json.load(f)
    
    # Jobs data for job counts
    jobs_df = pd.read_csv(base_dir / 'data/processed/jobs_labeled.csv')
    
    # Role skill profiles for top skills
    role_profiles = pd.read_csv(base_dir / 'skill_gap/role_skill_profiles.csv')
    
    # Role metadata for titles
    role_metadata = None
    meta_path = base_dir / 'data/processed/role_metadata.json'
    if meta_path.exists():
        with open(meta_path, 'r') as f:
            role_metadata = json.load(f)
    
    return career_ladders, jobs_df, role_profiles, role_metadata


def get_role_title(role_id: str, role_metadata: List[Dict], jobs_df: pd.DataFrame) -> str:
    """Get human-readable title for a role ID."""
    # Try role_metadata first
    if role_metadata:
        for r in role_metadata:
            if r.get('role_id') == role_id:
                return r.get('role_title', role_id)
    
    # Fallback to jobs data
    job_data = jobs_df[jobs_df['role_id'] == role_id]
    if not job_data.empty and 'role_title' in job_data.columns:
        return job_data['role_title'].mode().iloc[0] if len(job_data['role_title'].mode()) > 0 else role_id
    
    # Last resort: humanize role_id
    return role_id.replace('_', ' ').title()


def get_domain_display_name(domain_id: str) -> str:
    """Convert domain ID to display name."""
    mapping = {
        'SOFTWARE_ENGINEERING': 'Software Engineering',
        'FRONTEND_ENGINEERING': 'Frontend Engineering',
        'BACKEND_ENGINEERING': 'Backend Engineering',
        'FULLSTACK_ENGINEERING': 'Full-Stack Engineering',
        'DATA_ENGINEERING': 'Data Engineering',
        'DATA_SCIENCE': 'Data Science',
        'AI_ML': 'AI / Machine Learning',
        'DEVOPS_SRE': 'DevOps / SRE',
        'CLOUD_ENGINEERING': 'Cloud Engineering',
        'SECURITY': 'Security / Cybersecurity',
        'QA_TESTING': 'QA / Testing',
        'MOBILE_ENGINEERING': 'Mobile Development',
        'UI_UX_DESIGN': 'UI/UX Design',
        'PRODUCT_MANAGEMENT': 'Product Management',
        'BUSINESS_ANALYSIS': 'Business Analysis',
        'PROJECT_MANAGEMENT': 'Project Management',
        'TECHNICAL_WRITING': 'Technical Writing',
        'BLOCKCHAIN_WEB3': 'Blockchain / Web3',
        'GAME_DEVELOPMENT': 'Game Development',
        'EMBEDDED_SYSTEMS': 'Embedded Systems',
    }
    return mapping.get(domain_id, domain_id.replace('_', ' ').title())


def get_level_name(level: int) -> str:
    """Get level name based on position in career ladder."""
    names = {
        1: 'Entry Level / Intern',
        2: 'Junior',
        3: 'Mid-Level',
        4: 'Senior',
        5: 'Staff / Lead',
        6: 'Principal',
        7: 'Architect / Director',
    }
    return names.get(level, f'Level {level}')


def get_experience_range(level: int) -> str:
    """Get experience range based on level."""
    ranges = {
        1: '0-1 years',
        2: '1-3 years',
        3: '3-5 years',
        4: '5-8 years',
        5: '8-12 years',
        6: '12-15 years',
        7: '15+ years',
    }
    return ranges.get(level, f'{(level-1)*2}-{level*2} years')


def get_salary_range(level: int) -> str:
    """Get estimated salary range based on level (US market)."""
    ranges = {
        1: '$40k-$60k',
        2: '$60k-$85k',
        3: '$85k-$110k',
        4: '$110k-$140k',
        5: '$140k-$175k',
        6: '$175k-$220k',
        7: '$220k+',
    }
    return ranges.get(level, 'Varies')


def regenerate_career_ladders():
    """Main function to regenerate career ladders."""
    base_dir = Path(r"d:\SLIIT\Uni-Finder\career-service\career-ml")
    
    # Load data
    print("Loading data...")
    career_ladders, jobs_df, role_profiles, role_metadata = load_data(base_dir)
    
    # Get roles that exist in job data
    existing_roles = set(jobs_df['role_id'].unique()) if 'role_id' in jobs_df.columns else set()
    profile_roles = set(role_profiles['role_id'].unique())
    
    print(f"Found {len(existing_roles)} roles in job data")
    print(f"Found {len(profile_roles)} roles in skill profiles")
    
    enhanced_ladders = {}
    
    for domain_id, role_list in career_ladders.items():
        print(f"\nProcessing domain: {domain_id}")
        
        # Count total jobs in this domain
        domain_jobs = jobs_df[jobs_df['role_id'].isin(role_list)] if 'role_id' in jobs_df.columns else pd.DataFrame()
        total_jobs = len(domain_jobs)
        
        levels = []
        
        for idx, role_id in enumerate(role_list, start=1):
            # Check if role has data
            has_job_data = role_id in existing_roles
            has_skill_data = role_id in profile_roles
            
            # Get job count for this role
            role_jobs = jobs_df[jobs_df['role_id'] == role_id] if has_job_data else pd.DataFrame()
            job_count = len(role_jobs)
            
            # Get top skills for this role (from profiles if available, else empty)
            top_skills = []
            if has_skill_data:
                role_skill_data = role_profiles[role_profiles['role_id'] == role_id]
                top_skills = role_skill_data.nlargest(10, 'importance')['skill_id'].tolist()
            
            # Get sample job titles
            sample_titles = []
            if has_job_data and 'job_title_clean' in role_jobs.columns:
                sample_titles = role_jobs['job_title_clean'].value_counts().head(3).index.tolist()
            
            # Determine level number (position in ladder)
            level_num = min(idx, 7)  # Cap at 7 levels
            
            level_data = {
                'level': level_num,
                'level_name': get_level_name(level_num),
                'role_id': role_id,
                'role_title': get_role_title(role_id, role_metadata, jobs_df),
                'experience_range': get_experience_range(level_num),
                'avg_salary_range': get_salary_range(level_num),
                'sample_job_titles': sample_titles,
                'top_skills': top_skills,
                'skill_count': len(top_skills),
                'jobs_in_role': job_count,
                'has_job_data': has_job_data,
                'has_skill_data': has_skill_data,
            }
            
            levels.append(level_data)
        
        if levels:
            enhanced_ladders[domain_id] = {
                'domain_id': domain_id,
                'domain_name': get_domain_display_name(domain_id),
                'total_jobs_in_domain': total_jobs,
                'levels': levels,
                'alternate_paths': [],
                'related_domains': get_related_domains(domain_id),
            }
            print(f"  Added {len(levels)} levels")
        else:
            print(f"  SKIPPED (no roles with data)")
    
    # Save output
    output_path = base_dir / 'career_path/career_ladders_enhanced.json'
    with open(output_path, 'w') as f:
        json.dump(enhanced_ladders, f, indent=2)
    
    print(f"\n✅ Generated {len(enhanced_ladders)} career ladders at {output_path}")
    
    # Print summary
    print("\n📊 Summary:")
    for domain_id, data in enhanced_ladders.items():
        print(f"  {domain_id}: {len(data['levels'])} levels, {data['total_jobs_in_domain']} jobs")
    
    return enhanced_ladders


def get_related_domains(domain_id: str) -> List[str]:
    """Get related career domains."""
    relations = {
        'SOFTWARE_ENGINEERING': ['FRONTEND_ENGINEERING', 'BACKEND_ENGINEERING', 'FULLSTACK_ENGINEERING'],
        'FRONTEND_ENGINEERING': ['SOFTWARE_ENGINEERING', 'UI_UX_DESIGN', 'FULLSTACK_ENGINEERING'],
        'BACKEND_ENGINEERING': ['SOFTWARE_ENGINEERING', 'DATA_ENGINEERING', 'DEVOPS_SRE'],
        'FULLSTACK_ENGINEERING': ['SOFTWARE_ENGINEERING', 'FRONTEND_ENGINEERING', 'BACKEND_ENGINEERING'],
        'DATA_ENGINEERING': ['DATA_SCIENCE', 'BACKEND_ENGINEERING', 'AI_ML'],
        'DATA_SCIENCE': ['AI_ML', 'DATA_ENGINEERING', 'BUSINESS_ANALYSIS'],
        'AI_ML': ['DATA_SCIENCE', 'DATA_ENGINEERING', 'SOFTWARE_ENGINEERING'],
        'DEVOPS_SRE': ['CLOUD_ENGINEERING', 'BACKEND_ENGINEERING', 'SECURITY'],
        'CLOUD_ENGINEERING': ['DEVOPS_SRE', 'SECURITY', 'BACKEND_ENGINEERING'],
        'SECURITY': ['DEVOPS_SRE', 'CLOUD_ENGINEERING', 'SOFTWARE_ENGINEERING'],
        'QA_TESTING': ['SOFTWARE_ENGINEERING', 'DEVOPS_SRE'],
        'MOBILE_ENGINEERING': ['SOFTWARE_ENGINEERING', 'FRONTEND_ENGINEERING'],
        'UI_UX_DESIGN': ['FRONTEND_ENGINEERING', 'PRODUCT_MANAGEMENT'],
        'PRODUCT_MANAGEMENT': ['BUSINESS_ANALYSIS', 'PROJECT_MANAGEMENT', 'UI_UX_DESIGN'],
        'BUSINESS_ANALYSIS': ['DATA_SCIENCE', 'PRODUCT_MANAGEMENT', 'PROJECT_MANAGEMENT'],
        'PROJECT_MANAGEMENT': ['PRODUCT_MANAGEMENT', 'BUSINESS_ANALYSIS'],
    }
    return relations.get(domain_id, [])


if __name__ == '__main__':
    regenerate_career_ladders()
