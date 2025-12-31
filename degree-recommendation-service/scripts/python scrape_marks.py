import pandas as pd
from docx import Document
import os

def extract_cutoff_data(docx_path, output_csv_path):
    """
    Extracts cutoff marks from a Word document and saves them to a CSV file.
    
    Args:
    docx_path (str): Path to the source .docx file.
    output_csv_path (str): Path where the output .csv file will be saved.
    """
    
    if not os.path.exists(docx_path):
        print(f"Error: The file '{docx_path}' was not found.")
        return

    print(f"Processing file: {docx_path}...")
    
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"Error opening document: {e}")
        return

    all_records = []
    
    # Iterate through all tables in the document
    for i, table in enumerate(doc.tables):
        try:
            # 1. Analyze the Header Row (Row 0)
            # We clean up newlines and spaces to make headers readable
            header_row = table.rows[0]
            headers = [cell.text.strip().replace('\n', ' ') for cell in header_row.cells]
            
            # Validation: specific keywords ensure we are looking at a data table
            # (First header is usually empty or contains 'DISTRICT'/'COURSE')
            is_valid_table = False
            if "DISTRICT" in headers[0].upper() or "COURSE" in headers[0].upper():
                is_valid_table = True
            
            if not is_valid_table:
                # Some tables might be layout tables, skip them
                continue

            # 2. Iterate through Data Rows (Row 1 onwards)
            for row in table.rows[1:]:
                cells = row.cells
                
                # specific check to avoid empty rows
                if not cells:
                    continue
                
                # Column 0 is always the District
                district = cells[0].text.strip()
                
                # Skip rows that are empty or just repeat the header
                if not district or district.upper() == "DISTRICT" or "COURSE" in district.upper():
                    continue
                    
                # 3. Extract Marks for each Course (Column 1 onwards)
                for col_index in range(1, len(cells)):
                    # Safety check to ensure we don't go out of bounds of headers
                    if col_index >= len(headers):
                        break
                    
                    course_name = headers[col_index]
                    mark = cells[col_index].text.strip()
                    
                    # Add to our list of records
                    all_records.append({
                        "courseName": course_name,
                        "district": district,
                        "cutoff marks": mark
                    })
                    
        except Exception as e:
            print(f"Warning: Could not parse table {i}. Reason: {e}")
            continue

    # 4. Create DataFrame and Save to CSV
    if all_records:
        df = pd.DataFrame(all_records)
        
        # Save to CSV
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print("-" * 30)
        print(f"Success! Extracted {len(df)} records.")
        print(f"File saved to: {output_csv_path}")
        print("-" * 30)
        print("First 5 records found:")
        print(df.head())
    else:
        print("No data records were extracted. Please check the document structure.")

# --- Configuration ---
# Make sure this matches your file name exactly
input_file = "Cutoff marks_2024_2025-ENGLISH_Final.docx" 
output_file = "cutoff_marks_2024_2025.csv"

# --- Run the function ---
extract_cutoff_data(input_file, output_file)