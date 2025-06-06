import pdfminer.high_level
import docx2txt
import spacy
import re
import csv
import json

# Load the spaCy English NLP model
nlp = spacy.load("en_core_web_sm")

#Extract raw text from resume file which can be PDF or DOCX
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            return pdfminer.high_level.extract_text(f)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    else:
        return ""

#Extract name from the text using spaCy
def extract_name(text):
    doc = nlp(text)
    candidates = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON" and 1 < len(ent.text.split()) <= 3]

    false_positives = {"Problem Solving", "Stellarium"}  # Add any other common false positives here

    for candidate in candidates:
        # Remove newlines & extra spaces
        clean_candidate = " ".join(candidate.split())
        
        # Filter false positives
        if clean_candidate in false_positives:
            continue
        
        # Check if contain mostly alphabetic characters 
        if all(word.isalpha() for word in clean_candidate.split()):
            return clean_candidate

    return None


#Extract email using regex
def extract_email(text):
    match = re.search(r'\w+@\w+\.\w+', text)
    return match.group(0) if match else None

#Extract phone using same thing that is regex
def extract_phone(text):
    match = re.search(r'\d{10}', text)
    return match.group(0) if match else None

#Extract skills from text given a skills list saved in a text file containing prementioned skills
def extract_skills(text, skill_set):
    text = text.lower()
    found = set()  # use set to avoid duplicates
    for skill in skill_set:
        skill_lower = skill.lower()
        # Match whole word 
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            found.add(skill)
    return list(found)

#Save extracted data to CSV
def save_to_csv(data, filename="parsed_resume.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["Name", "Email", "Phone", "Skills"])
        # Write data row
        writer.writerow([data["name"], data["email"], data["phone"], ", ".join(data["skills"])])

#Save extracted data to JSON
def save_to_json(data, filename="parsed_resume.json"):
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Main execution
if __name__ == "__main__":
    text = extract_text(r"INSERT FILE PATH OF DESIRED RESUME WHOSE CONTENTS ARE TO BE EXTRACTED.pdf")

    with open("skills.txt", "r") as f:
        skills_list = [line.strip() for line in f.readlines()]

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text, skills_list)

    parsed_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills
    }

    # Print to console
    print("Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("Skills:", skills)

    # Save results
    save_to_csv(parsed_data)
    save_to_json(parsed_data)
    print("Data saved to parsed_resume.csv and parsed_resume.json")