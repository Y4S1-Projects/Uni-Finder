"""
Career-to-Degree Mapping Layer
Maps career aspirations and verbs to academic fields and job roles.
This fixes the semantic gap where students express goals like "I want to be X"
instead of using academic terminology.
"""

from typing import Dict, List, Set
import re


class CareerMapper:
    """
    Expands student queries with hidden career intent by mapping
    aspirational language to concrete job roles and academic fields.
    """

    # Career aspiration patterns with their target keywords
    CAREER_MAPPINGS: Dict[str, List[str]] = {
        # Technology & Computing
        "big data": [
            "Data Scientist",
            "Data Engineer",
            "Data Analyst",
            "Machine Learning Engineer",
            "Analytics",
        ],
        "artificial intelligence": [
            "AI Engineer",
            "Machine Learning Engineer",
            "Data Scientist",
            "Research Scientist",
        ],
        "ai": [
            "AI Engineer",
            "Machine Learning Engineer",
            "Data Scientist",
            "Deep Learning",
        ],
        "machine learning": [
            "ML Engineer",
            "Data Scientist",
            "AI Researcher",
            "Algorithm Engineer",
        ],
        "programming": [
            "Software Developer",
            "Software Engineer",
            "Programmer",
            "Full Stack Developer",
        ],
        "coding": [
            "Software Developer",
            "Software Engineer",
            "Web Developer",
            "App Developer",
        ],
        "software": [
            "Software Engineer",
            "Software Developer",
            "Systems Analyst",
            "DevOps Engineer",
        ],
        "app development": [
            "Mobile Developer",
            "App Developer",
            "iOS Developer",
            "Android Developer",
        ],
        "web development": [
            "Web Developer",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
        ],
        "cybersecurity": [
            "Security Analyst",
            "Penetration Tester",
            "Security Engineer",
            "Ethical Hacker",
        ],
        "hacking": [
            "Cybersecurity Specialist",
            "Ethical Hacker",
            "Security Analyst",
            "Penetration Tester",
        ],
        "networks": [
            "Network Engineer",
            "Network Administrator",
            "Systems Engineer",
            "IT Infrastructure",
        ],
        "databases": [
            "Database Administrator",
            "Data Engineer",
            "Backend Developer",
            "SQL Developer",
        ],
        "cloud": [
            "Cloud Engineer",
            "Cloud Architect",
            "DevOps Engineer",
            "AWS Specialist",
        ],
        "game": [
            "Game Developer",
            "Game Designer",
            "Unity Developer",
            "Graphics Programmer",
        ],
        # Business & Finance
        "business": [
            "Business Manager",
            "Entrepreneur",
            "Business Analyst",
            "Management Consultant",
        ],
        "entrepreneur": [
            "Business Owner",
            "Startup Founder",
            "Business Manager",
            "Innovation Manager",
        ],
        "management": [
            "Manager",
            "Operations Manager",
            "Business Manager",
            "Project Manager",
        ],
        "finance": [
            "Financial Analyst",
            "Finance Manager",
            "Investment Analyst",
            "Financial Planner",
        ],
        "accounting": [
            "Accountant",
            "Auditor",
            "Tax Consultant",
            "Financial Accountant",
        ],
        "marketing": [
            "Marketing Manager",
            "Brand Manager",
            "Digital Marketer",
            "Marketing Strategist",
        ],
        "sales": [
            "Sales Manager",
            "Business Development",
            "Account Manager",
            "Sales Executive",
        ],
        "human resources": [
            "HR Manager",
            "Talent Acquisition",
            "HR Consultant",
            "People Operations",
        ],
        "banking": [
            "Bank Manager",
            "Investment Banker",
            "Financial Analyst",
            "Credit Analyst",
        ],
        "stock market": [
            "Stock Broker",
            "Investment Analyst",
            "Portfolio Manager",
            "Trader",
        ],
        # Healthcare & Medicine
        "doctor": [
            "Medical Doctor",
            "Physician",
            "Surgeon",
            "General Practitioner",
            "Medical Officer",
        ],
        "medicine": [
            "Medical Doctor",
            "Healthcare Professional",
            "Physician",
            "Surgeon",
        ],
        "surgeon": [
            "Surgeon",
            "Medical Specialist",
            "Operating Surgeon",
            "Surgical Consultant",
        ],
        "nurse": ["Nurse", "Registered Nurse", "Healthcare Provider", "Clinical Nurse"],
        "nursing": ["Nurse", "Healthcare Assistant", "Clinical Nurse", "Patient Care"],
        "patients": [
            "Healthcare Professional",
            "Medical Practitioner",
            "Nurse",
            "Caregiver",
        ],
        "healthcare": [
            "Healthcare Professional",
            "Medical Officer",
            "Health Administrator",
            "Clinical Officer",
        ],
        "pharmacy": [
            "Pharmacist",
            "Clinical Pharmacist",
            "Pharmaceutical Scientist",
            "Drug Safety Officer",
        ],
        "dentist": ["Dentist", "Dental Surgeon", "Orthodontist", "Dental Consultant"],
        "physiotherapy": [
            "Physiotherapist",
            "Physical Therapist",
            "Rehabilitation Specialist",
            "Sports Therapist",
        ],
        "psychology": [
            "Psychologist",
            "Clinical Psychologist",
            "Counselor",
            "Therapist",
        ],
        # Education & Teaching
        "teach": ["Teacher", "Lecturer", "Educator", "Academic", "Instructor"],
        "teacher": ["Teacher", "Educator", "School Teacher", "Lecturer", "Professor"],
        "educate": ["Educator", "Teacher", "Academic", "Instructor", "Trainer"],
        "lecturer": [
            "Lecturer",
            "University Teacher",
            "Academic",
            "Professor",
            "Instructor",
        ],
        "professor": [
            "Professor",
            "Academic",
            "Researcher",
            "University Lecturer",
            "Scholar",
        ],
        "training": [
            "Trainer",
            "Corporate Trainer",
            "Learning Development",
            "Education Specialist",
        ],
        "children": [
            "Teacher",
            "Early Childhood Educator",
            "School Teacher",
            "Childcare Professional",
        ],
        "next generation": [
            "Teacher",
            "Educator",
            "Youth Worker",
            "Academic",
            "Mentor",
        ],
        # Engineering
        "engineer": [
            "Engineer",
            "Engineering Consultant",
            "Technical Engineer",
            "Design Engineer",
        ],
        "machines": [
            "Mechanical Engineer",
            "Mechatronics Engineer",
            "Manufacturing Engineer",
            "Automation Engineer",
        ],
        "mechanical": [
            "Mechanical Engineer",
            "Design Engineer",
            "Manufacturing Engineer",
            "Automotive Engineer",
        ],
        "electrical": [
            "Electrical Engineer",
            "Electronics Engineer",
            "Power Engineer",
            "Control Systems Engineer",
        ],
        "electronics": [
            "Electronics Engineer",
            "Embedded Systems Engineer",
            "Circuit Designer",
            "Hardware Engineer",
        ],
        "circuits": [
            "Electronics Engineer",
            "Circuit Designer",
            "Embedded Engineer",
            "Hardware Developer",
        ],
        "civil": [
            "Civil Engineer",
            "Structural Engineer",
            "Construction Engineer",
            "Infrastructure Engineer",
        ],
        "construction": [
            "Civil Engineer",
            "Construction Manager",
            "Project Engineer",
            "Site Engineer",
        ],
        "bridges": [
            "Civil Engineer",
            "Structural Engineer",
            "Bridge Engineer",
            "Infrastructure Engineer",
        ],
        "buildings": [
            "Civil Engineer",
            "Structural Engineer",
            "Architect",
            "Construction Engineer",
        ],
        "chemical": [
            "Chemical Engineer",
            "Process Engineer",
            "Petrochemical Engineer",
            "Industrial Chemist",
        ],
        "manufacturing": [
            "Manufacturing Engineer",
            "Production Engineer",
            "Industrial Engineer",
            "Process Engineer",
        ],
        # Design & Architecture
        "design buildings": [
            "Architect",
            "Architectural Designer",
            "Building Designer",
            "Urban Planner",
        ],
        "architecture": [
            "Architect",
            "Architectural Designer",
            "Urban Designer",
            "Interior Architect",
        ],
        "architect": [
            "Architect",
            "Architectural Consultant",
            "Building Designer",
            "Urban Designer",
        ],
        "urban planning": [
            "Urban Planner",
            "City Planner",
            "Regional Planner",
            "Spatial Planner",
        ],
        "interior": [
            "Interior Designer",
            "Interior Architect",
            "Space Designer",
            "Design Consultant",
        ],
        "graphic design": [
            "Graphic Designer",
            "Visual Designer",
            "Brand Designer",
            "Creative Designer",
        ],
        "ui": ["UI Designer", "UX Designer", "Product Designer", "Interface Designer"],
        "ux": [
            "UX Designer",
            "User Experience Designer",
            "Product Designer",
            "Interaction Designer",
        ],
        # Agriculture & Environment
        "farming": [
            "Agricultural Officer",
            "Farm Manager",
            "Agronomist",
            "Agricultural Scientist",
        ],
        "agriculture": [
            "Agricultural Scientist",
            "Agronomist",
            "Crop Specialist",
            "Agricultural Engineer",
        ],
        "crops": [
            "Agronomist",
            "Crop Scientist",
            "Agricultural Specialist",
            "Plant Scientist",
        ],
        "sustainable": [
            "Sustainability Consultant",
            "Environmental Scientist",
            "Green Technology Specialist",
        ],
        "environment": [
            "Environmental Scientist",
            "Environmental Consultant",
            "Conservation Officer",
            "Ecologist",
        ],
        "animals": [
            "Veterinarian",
            "Animal Scientist",
            "Livestock Manager",
            "Veterinary Surgeon",
        ],
        "veterinary": [
            "Veterinarian",
            "Veterinary Surgeon",
            "Animal Health Officer",
            "Vet Scientist",
        ],
        # Law & Legal
        "lawyer": [
            "Lawyer",
            "Attorney",
            "Legal Advisor",
            "Legal Consultant",
            "Advocate",
        ],
        "law": ["Lawyer", "Legal Professional", "Attorney", "Legal Consultant"],
        "legal": ["Legal Officer", "Lawyer", "Legal Advisor", "Compliance Officer"],
        "court": ["Lawyer", "Attorney", "Barrister", "Legal Practitioner"],
        "justice": ["Legal Officer", "Lawyer", "Judicial Officer", "Legal Consultant"],
        # Media & Communication
        "journalism": ["Journalist", "Reporter", "News Writer", "Media Professional"],
        "reporter": ["Reporter", "Journalist", "News Correspondent", "Media Analyst"],
        "media": [
            "Media Professional",
            "Content Creator",
            "Journalist",
            "Communications Officer",
        ],
        "photography": [
            "Photographer",
            "Visual Artist",
            "Media Photographer",
            "Photo Journalist",
        ],
        "video": ["Videographer", "Video Editor", "Content Creator", "Film Maker"],
        "content creation": [
            "Content Creator",
            "Digital Content Specialist",
            "Social Media Manager",
        ],
        # Science & Research
        "research": [
            "Researcher",
            "Research Scientist",
            "Academic Researcher",
            "Data Analyst",
        ],
        "scientist": [
            "Scientist",
            "Research Scientist",
            "Laboratory Scientist",
            "Scientific Officer",
        ],
        "laboratory": [
            "Lab Technician",
            "Laboratory Scientist",
            "Research Assistant",
            "Analyst",
        ],
        "physics": [
            "Physicist",
            "Research Physicist",
            "Scientific Officer",
            "Physics Teacher",
        ],
        "chemistry": [
            "Chemist",
            "Chemical Analyst",
            "Laboratory Scientist",
            "Research Chemist",
        ],
        "biology": [
            "Biologist",
            "Biological Scientist",
            "Research Biologist",
            "Microbiologist",
        ],
        "mathematics": [
            "Mathematician",
            "Data Analyst",
            "Statistician",
            "Quantitative Analyst",
        ],
        "statistics": [
            "Statistician",
            "Data Analyst",
            "Statistical Analyst",
            "Data Scientist",
        ],
        # Hospitality & Tourism
        "hotel": [
            "Hotel Manager",
            "Hospitality Manager",
            "Guest Relations",
            "Hotel Operations",
        ],
        "tourism": [
            "Tourism Officer",
            "Travel Consultant",
            "Tourism Manager",
            "Tour Operator",
        ],
        "chef": ["Chef", "Culinary Expert", "Head Chef", "Food Scientist"],
        "cooking": [
            "Chef",
            "Culinary Specialist",
            "Food Preparation",
            "Restaurant Manager",
        ],
        # General Career Verbs
        "manage": [
            "Manager",
            "Management Professional",
            "Operations Manager",
            "Administrator",
        ],
        "analyze": ["Analyst", "Data Analyst", "Business Analyst", "Research Analyst"],
        "build": ["Engineer", "Developer", "Construction Professional", "Maker"],
        "create": ["Creator", "Designer", "Developer", "Artist"],
        "solve": ["Problem Solver", "Analyst", "Consultant", "Engineer"],
        "help people": [
            "Healthcare Professional",
            "Social Worker",
            "Counselor",
            "Teacher",
        ],
    }

    # Academic field keywords for direct boosting
    ACADEMIC_FIELDS: Dict[str, List[str]] = {
        "computer science": [
            "Computer Science",
            "Computing",
            "IT",
            "Software Engineering",
        ],
        "information technology": [
            "IT",
            "Information Technology",
            "Computer Science",
            "Systems",
        ],
        "data science": ["Data Science", "Analytics", "Statistics", "Machine Learning"],
        "engineering": ["Engineering", "Technical", "Applied Science"],
        "medicine": ["Medicine", "Medical", "Healthcare", "Clinical"],
        "business": ["Business", "Management", "Commerce", "Administration"],
        "education": ["Education", "Teaching", "Pedagogy", "Training"],
        "law": ["Law", "Legal Studies", "Jurisprudence"],
        "agriculture": ["Agriculture", "Agricultural Science", "Agronomy"],
        "architecture": ["Architecture", "Architectural Design", "Building Design"],
    }

    def __init__(self):
        """Initialize the career mapper with compiled regex patterns."""
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Pre-compile regex patterns for efficiency."""
        patterns = {}
        for keyword in self.CAREER_MAPPINGS.keys():
            # Use word boundaries to match whole words
            patterns[keyword] = re.compile(
                r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE
            )
        return patterns

    def expand_query(self, student_query: str) -> str:
        """
        Expand student query with inferred career keywords.

        Args:
            student_query: Original student interest/aspiration text

        Returns:
            Expanded query with appended career terms
        """
        matched_careers: Set[str] = set()
        matched_fields: Set[str] = set()

        query_lower = student_query.lower()

        # Find matching career terms
        for keyword, career_terms in self.CAREER_MAPPINGS.items():
            if keyword in query_lower:
                matched_careers.update(career_terms)

        # Find matching academic fields
        for field, field_terms in self.ACADEMIC_FIELDS.items():
            if field in query_lower:
                matched_fields.update(field_terms)

        # Build expanded query
        expanded = student_query

        if matched_careers:
            career_str = ", ".join(
                sorted(matched_careers)[:5]
            )  # Limit to top 5 to avoid oversaturation
            expanded += f". Target Careers: {career_str}"

        if matched_fields:
            field_str = ", ".join(sorted(matched_fields)[:3])
            expanded += f". Academic Fields: {field_str}"

        return expanded

    def get_career_keywords(self, query: str) -> List[str]:
        """
        Extract career keywords from query without modifying it.
        Useful for debugging and logging.
        """
        matched = set()
        query_lower = query.lower()

        for keyword, career_terms in self.CAREER_MAPPINGS.items():
            if keyword in query_lower:
                matched.update(career_terms[:3])  # Top 3 per match

        return sorted(matched)
