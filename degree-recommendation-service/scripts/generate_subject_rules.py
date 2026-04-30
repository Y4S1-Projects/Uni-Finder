import csv
import json
import time
import re
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not api_key:
    print("Error: GOOGLE_GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "University_Courses_Dataset.csv"
OUTPUT_PATH = DATA_DIR / "course_subject_rules.json"

PROMPT_TEMPLATE = """
You are an expert system that converts natural language degree requirements into strict Boolean logic Abstract Syntax Trees (ASTs) in JSON.

I will provide a JSON object where the keys are course codes and the values are the raw natural language A/L Subject Requirements.
Your task is to convert each requirement into a structured JSON AST representing the eligibility logic.

The JSON AST must use only the following node types:
1. {"type": "AND", "operands": [node1, node2, ...]}
2. {"type": "OR", "operands": [node1, node2, ...]}
3. {"type": "MIN_COUNT", "count": N, "operands": [node1, node2, ...]} - Use this for rules like "2 from these subjects"
4. {"type": "SUBJECT", "name": "lowercase_standardized_subject_name"}
5. {"type": "ANY_SUBJECT"} - Use this for rules like "any other subject" or "any 3 A/L subjects"
6. {"type": "STREAM", "name": "lowercase_stream_name"} - Use this if a rule mentions an entire stream instead of subjects (e.g., "Arts Stream")

IMPORTANT RULES:
- The output MUST be a valid JSON object where keys are the course codes and values are the AST.
- DO NOT output any markdown, code blocks, or text outside of the JSON object. Just the raw JSON.
- Standardize all subject names to lower case (e.g., "combined mathematics", "information & communication technology", "chemistry").
- Resolve abbreviations: "Math" -> "mathematics", "Agri Sci" -> "agricultural science", "ICT" -> "information & communication technology", "Bio" -> "biology", "Chem" -> "chemistry".
- If the requirement is empty or "N/A" or "None", return {"type": "ANY_SUBJECT"}.

Input:
{input_json}
"""


def process_batch(batch_dict):
    """Process a batch of course requirements using Gemini with retries."""
    prompt = PROMPT_TEMPLATE.replace("{input_json}", json.dumps(batch_dict, indent=2))

    while True:
        try:
            print(f"  Sending {len(batch_dict)} courses to Gemini...")
            response = model.generate_content(prompt)
            text = response.text

            # Clean up potential markdown code blocks
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"^```\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            return json.loads(text)

        except json.JSONDecodeError as e:
            print(f"  Error: Gemini returned invalid JSON: {e}")
            print(f"  Response was: {text[:200]}...")
            return {}
        except Exception as e:
            error_str = str(e)
            print(f"  API Error: {error_str[:200]}...")

            # Parse wait time from "retry_delay { seconds: X }"
            match = re.search(
                r"retry_delay.*?seconds:\s*(\d+)", error_str, re.DOTALL | re.IGNORECASE
            )
            if match:
                delay = int(match.group(1)) + 5
            elif "429" in error_str:
                delay = 60
            else:
                return {}

            print(f"  Waiting {delay} seconds before retry...")
            time.sleep(delay)


def main():
    print("Loading CSV data...")
    courses_dict = {}

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Course Code", "").strip()
            # Normalize course code to 3 digits like backend does
            try:
                code_norm = f"{int(code):03d}"
            except ValueError:
                code_norm = code

            req = row.get("A/L Subject Requirements", "").strip()

            if code_norm and code_norm not in courses_dict:
                courses_dict[code_norm] = req

    print(f"Found {len(courses_dict)} total courses.")

    # Process in batches of 20 to avoid token limits
    batch_size = 20
    all_codes = list(courses_dict.keys())

    final_rules = {}

    for i in range(0, len(all_codes), batch_size):
        batch_codes = all_codes[i : i + batch_size]
        batch_dict = {c: courses_dict[c] for c in batch_codes}

        print(
            f"Processing batch {i//batch_size + 1}/{(len(all_codes) + batch_size - 1)//batch_size}..."
        )

        result = process_batch(batch_dict)
        if result:
            final_rules.update(result)

        # Small delay between batches to respect quotas
        time.sleep(2)

    # Ensure all codes have an entry (fallback for failures)
    for code in all_codes:
        if code not in final_rules:
            print(
                f"Warning: Course {code} failed to process. Using ANY_SUBJECT fallback."
            )
            final_rules[code] = {"type": "ANY_SUBJECT"}

    print(f"Writing {len(final_rules)} rules to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_rules, f, indent=2)

    print("Done! Boolean Logic AST successfully generated.")


if __name__ == "__main__":
    main()
