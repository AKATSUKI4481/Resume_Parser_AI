# 📦 Original Resume Parser Code (Unchanged Logic)
import pdfminer.high_level
import docx2txt
import spacy
import re
import csv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            return pdfminer.high_level.extract_text(f)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    else:
        return ""

def extract_name(text):
    doc = nlp(text)
    candidates = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON" and 1 < len(ent.text.split()) <= 3]
    false_positives = {"Problem Solving", "Stellarium"}
    for candidate in candidates:
        clean_candidate = " ".join(candidate.split())
        if clean_candidate in false_positives:
            continue
        if all(word.isalpha() for word in clean_candidate.split()):
            return clean_candidate
    return None

def extract_email(text):
    match = re.search(r'\w+@\w+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\d{10}', text)
    return match.group(0) if match else None

def extract_skills(text, skill_set):
    text = text.lower()
    found = set()
    for skill in skill_set:
        skill_lower = skill.lower()
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            found.add(skill)
    return list(found)

def save_to_csv(data, filename="parsed_resume.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "Phone", "Skills"])
        writer.writerow([data["name"], data["email"], data["phone"], ", ".join(data["skills"])])

def save_to_json(data, filename="parsed_resume.json"):
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# 🖼️ GUI Interface (Only Added Below)
def run_parser_gui():
    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")])
        if file_path:
            try:
                text = extract_text(file_path)

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

                save_to_csv(parsed_data)
                save_to_json(parsed_data)

                output_area.delete("1.0", tk.END)
                output_area.insert(tk.END, f"📄 Name: {name}\n")
                output_area.insert(tk.END, f"✉️ Email: {email}\n")
                output_area.insert(tk.END, f"📞 Phone: {phone}\n")
                output_area.insert(tk.END, f"🛠️ Skills: {', '.join(skills)}\n\n")
                output_area.insert(tk.END, "✅ Data saved to parsed_resume.csv and parsed_resume.json")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse file:\n{e}")

    # Tkinter GUI Layout
    root = tk.Tk()
    root.title("AI Resume Parser")
    root.geometry("600x400")
    root.resizable(False, False)

    tk.Label(root, text="📁 Select a Resume File (.pdf / .docx)", font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Browse Resume", font=("Arial", 12), command=browse_file, bg="#4CAF50", fg="white", padx=10, pady=5).pack()

    output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10), height=15, width=70)
    output_area.pack(pady=10)

    root.mainloop()

# Launch GUI
if __name__ == "__main__":
    run_parser_gui()

