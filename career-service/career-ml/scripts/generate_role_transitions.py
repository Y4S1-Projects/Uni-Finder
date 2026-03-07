import json
import pandas as pd
from pathlib import Path

def generate_role_transitions():
    base_dir = Path(r"d:\SLIIT\Uni-Finder\career-ml")
    ladders_file = base_dir / 'career_path' / 'career_ladders_enhanced.json'
    role_skills_df = pd.read_csv(base_dir / 'skill_gap/role_skill_profiles.csv')
    
    with open(ladders_file, 'r') as f:
        ladders = json.load(f)
        
    transitions = []
    
    for domain_id, ladder in ladders.items():
        levels = ladder['levels']
        
        for i in range(len(levels) - 1):
            curr_level = levels[i]
            next_level = levels[i+1]
            
            # Get skill profiles for next level
            next_skills_data = role_skills_df[role_skills_df['role_id'] == next_level['role_id']]
            
            required_skills = []
            nice_to_have = []
            
            for _, row in next_skills_data.iterrows():
                skill_id = row['skill_id']
                importance = row['importance']
                
                # If skill is not in current level
                if skill_id not in curr_level['top_skills']:
                    if importance > 0.1:
                        required_skills.append(skill_id)
                    elif importance >= 0.05:
                        nice_to_have.append(skill_id)
            
            gap_size = len(required_skills)
            if gap_size < 5:
                difficulty = "easy"
            elif gap_size <= 10:
                difficulty = "medium"
            else:
                difficulty = "hard"
                
            transitions.append({
                'current_role_id': curr_level['role_id'],
                'next_role_id': next_level['role_id'],
                'current_level': curr_level['level'],
                'next_level': next_level['level'],
                'domain': domain_id,
                'required_new_skills': '|'.join(required_skills),
                'nice_to_have_skills': '|'.join(nice_to_have),
                'estimated_time_months': 6,
                'difficulty': difficulty
            })
            
    df = pd.DataFrame(transitions)
    output_path = base_dir / 'career_path' / 'role_level_transitions.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(transitions)} role transitions at {output_path}")

if __name__ == '__main__':
    generate_role_transitions()
