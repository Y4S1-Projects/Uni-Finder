import pandas as pd
import json
from collections import defaultdict
import re
from pathlib import Path

def generate_enhanced_career_ladders():
    base_dir = Path(r"d:\SLIIT\Uni-Finder\career-ml")
    # Load data
    jobs_df = pd.read_csv(base_dir / 'data/processed/jobs_labeled.csv')
    role_skills_df = pd.read_csv(base_dir / 'skill_gap/role_skill_profiles.csv')
    skills_df = pd.read_csv(base_dir / 'data/processed/skills_cleaned.csv')
    
    # Define level patterns and domains
    level_patterns = {
        1: r'\b(intern|trainee|fresher)\b',
        2: r'\b(junior|jr|associate|entry)\b',
        3: r'^(?!.*(senior|sr|lead|principal|staff|architect))',
        4: r'\b(senior|sr)\b',
        5: r'\b(lead|staff|principal)\b',
        6: r'\b(architect|chief|distinguished|director)\b'
    }
    
    domains = {
        'SOFTWARE_ENGINEERING': ['software', 'developer', 'engineer', 'backend', 'frontend', 'fullstack'],
        'DATA': ['data', 'analyst', 'analytics', 'bi', 'business intelligence'],
        'AI_ML': ['ai', 'ml', 'machine learning', 'data scientist'],
        'DEVOPS': ['devops', 'sre', 'infrastructure', 'cloud engineer'],
        'QA': ['qa', 'test', 'quality assurance', 'qc'],
        'SECURITY': ['security', 'cybersecurity', 'infosec'],
        'MOBILE': ['mobile', 'android', 'ios', 'react native'],
        'UIUX': ['ui', 'ux', 'designer', 'product design'],
        'PRODUCT': ['product manager', 'product owner', 'pm'],
        'CLOUD': ['aws', 'azure', 'gcp', 'cloud architect']
    }
    
    career_ladders = {}
    
    # Ensure job_title_clean exists
    if 'job_title_clean' not in jobs_df.columns and 'job_title' in jobs_df.columns:
        jobs_df['job_title_clean'] = jobs_df['job_title'].astype(str)
        
    for domain_id, keywords in domains.items():
        # Filter jobs for this domain
        domain_jobs = jobs_df[jobs_df['job_title_clean'].str.lower().str.contains('|'.join(keywords), na=False)]
        
        if len(domain_jobs) == 0:
            continue
            
        levels = []
        for level_num in range(1, 7):
            # Extract jobs matching this level pattern
            if level_num == 3:
                # Mid-level: no senior/lead/etc
                level_jobs = domain_jobs[
                    ~domain_jobs['job_title_clean'].str.lower().str.contains('senior|lead|principal|staff|architect|intern|trainee|junior|jr', na=False)
                ]
            else:
                pattern = level_patterns[level_num]
                level_jobs = domain_jobs[domain_jobs['job_title_clean'].str.lower().str.contains(pattern, na=False, regex=True)]
            
            if len(level_jobs) == 0:
                continue
            
            # Get most common role_id for this level
            role_id = level_jobs['role_id'].mode()[0] if len(level_jobs) > 0 else f"{domain_id}_L{level_num}"
            role_title = level_jobs['role_title'].mode()[0] if len(level_jobs) > 0 else f"Level {level_num} {domain_id.replace('_', ' ')}"
            
            # Get top skills for this role
            role_skill_data = role_skills_df[role_skills_df['role_id'] == role_id]
            top_skills = role_skill_data.nlargest(10, 'importance')['skill_id'].tolist()
            
            # Sample job titles
            sample_titles = level_jobs['job_title_clean'].value_counts().head(3).index.tolist()
            
            level_data = {
                'level': level_num,
                'level_name': ['Entry Level', 'Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal'][level_num-1],
                'role_id': role_id,
                'role_title': role_title,
                'experience_range': ['0-1 years', '1-3 years', '3-5 years', '5-8 years', '8-12 years', '12+ years'][level_num-1],
                'avg_salary_range': ['$30k-$50k', '$50k-$75k', '$75k-$100k', '$100k-$130k', '$130k-$165k', '$165k-$220k+'][level_num-1],
                'sample_job_titles': sample_titles,
                'top_skills': top_skills,
                'skill_count': len(top_skills),
                'jobs_in_role': len(level_jobs)
            }
            
            levels.append(level_data)
        
        if len(levels) > 0:
            career_ladders[domain_id] = {
                'domain_id': domain_id,
                'domain_name': domain_id.replace('_', ' ').title(),
                'total_jobs_in_domain': len(domain_jobs),
                'levels': levels,
                'alternate_paths': [],
                'related_domains': []
            }
    
    # Save to JSON
    output_path = base_dir / 'career_path/career_ladders_enhanced.json'
    with open(output_path, 'w') as f:
        json.dump(career_ladders, f, indent=2)
    
    print(f"Generated {len(career_ladders)} career ladders at {output_path}")
    return career_ladders

if __name__ == '__main__':
    generate_enhanced_career_ladders()
