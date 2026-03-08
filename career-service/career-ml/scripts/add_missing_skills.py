"""
Add unmapped skills to appropriate role profiles.

These 12 skills exist in skills_cleaned.csv but are not assigned to any role:
- SK014 (c) - Backend, SE
- SK127 (bgp), SK128 (ospf), SK221 (eigrp), SK283 (stp), SK297 (hsrp) - DevOps/SRE  
- SK169 (network configuration maintenance), SK276 (cisco routers) - DevOps/SRE
- SK235 (ipsec) - DevOps/Security
- SK232 (senior network), SK280 (senior web) - Ambiguous, skip
- SK300 (opencart) - Fullstack/Backend
"""

import pandas as pd
from pathlib import Path


def add_missing_skills():
    base_dir = Path(r"d:\SLIIT\Uni-Finder\career-service\career-ml")
    
    # Load current role profiles
    profile_path = base_dir / 'skill_gap/role_skill_profiles.csv'
    df = pd.read_csv(profile_path)
    
    print(f"Current profile count: {len(df)}")
    print(f"Current skill count: {df['skill_id'].nunique()}")
    
    # Define mappings: skill_id -> [(role_id, importance), ...]
    skill_to_roles = {
        # C programming language - common in systems/backend work
        'SK014': [
            ('JR_BE_DEV', 0.20),
            ('JR_SE', 0.15),
            ('DEVOPS_TRAINEE', 0.10),
        ],
        # Networking protocols (bgp, ospf, eigrp, stp, hsrp) - DevOps/SRE
        'SK127': [('DEVOPS_TRAINEE', 0.05), ('JR_SYS_ADMIN', 0.08)],  # bgp
        'SK128': [('DEVOPS_TRAINEE', 0.05), ('JR_SYS_ADMIN', 0.08)],  # ospf
        'SK221': [('DEVOPS_TRAINEE', 0.04), ('JR_SYS_ADMIN', 0.06)],  # eigrp
        'SK283': [('DEVOPS_TRAINEE', 0.04), ('JR_SYS_ADMIN', 0.05)],  # stp
        'SK297': [('DEVOPS_TRAINEE', 0.04), ('JR_SYS_ADMIN', 0.05)],  # hsrp
        # Network maintenance - DevOps
        'SK169': [('DEVOPS_TRAINEE', 0.06), ('JR_SYS_ADMIN', 0.10)],  # network config
        'SK276': [('DEVOPS_TRAINEE', 0.05), ('JR_SYS_ADMIN', 0.08)],  # cisco routers
        # IPSec - Security domain
        'SK235': [('DEVOPS_TRAINEE', 0.05)],  # ipsec
        # OpenCart - E-commerce, fullstack/backend
        'SK300': [('JR_FS_DEV', 0.05), ('JR_BE_DEV', 0.04)],  # opencart
        # Skip SK232 (senior network) and SK280 (senior web) - too ambiguous
    }
    
    new_rows = []
    for skill_id, role_mappings in skill_to_roles.items():
        for role_id, importance in role_mappings:
            # Check if this combination already exists
            exists = len(df[(df['skill_id'] == skill_id) & (df['role_id'] == role_id)]) > 0
            if not exists:
                new_rows.append({
                    'role_id': role_id,
                    'skill_id': skill_id,
                    'frequency': 1,  # At least 1 occurrence
                    'importance': importance,
                })
                print(f"  Adding {skill_id} to {role_id} (importance: {importance})")
    
    if new_rows:
        new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        new_df.to_csv(profile_path, index=False)
        print(f"\n✅ Added {len(new_rows)} new skill-role mappings")
        print(f"New profile count: {len(new_df)}")
        print(f"New skill count: {new_df['skill_id'].nunique()}")
    else:
        print("No new skills to add")
    
    return len(new_rows)


if __name__ == '__main__':
    add_missing_skills()
