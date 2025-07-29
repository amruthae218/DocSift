import re
import spacy
from rapidfuzz import fuzz

nlp = spacy.load("en_core_web_sm")

# Common hospital/clinic/diagnostic center names
KNOWN_HOSPITALS = [
    "Apollo", "Fortis", "Kauvery", "Global", "MIOT", "Vijaya",
    "Manipal", "CMC", "Aarthi", "SRMC", "Billroth", "Medall", "Prashanth"
]

def regex_scrub(text: str) -> str:
    """Scrub using regex patterns and known labels."""
    patterns = [
        r"\b\d{12}\b",                                 # Aadhaar
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",                  # PAN
        r"\b\d{10}\b",                                 # 10-digit phone
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # Email
        r"(?i)(?<=Patient Name:)[^\n]+",               # "Patient Name" line
        r"(?i)\b(name|patient|attendee)[\s:]*[a-zA-Z .]+\b"  # General name patterns
    ]

    for pat in patterns:
        text = re.sub(pat, " [REDACTED]", text)
    return text

def fuzzy_hospital_scrub(text: str, threshold=85) -> str:
    """Scrub known hospital/clinic names using fuzzy matching line by line."""
    lines = text.splitlines()
    scrubbed_lines = []

    for line in lines:
        modified = line
        for name in KNOWN_HOSPITALS:
            if fuzz.partial_ratio(name.lower(), line.lower()) > threshold:
                modified = re.sub(rf"(?i)\b\S*{name}\S*\b", "[REDACTED]", modified)
        scrubbed_lines.append(modified)

    return "\n".join(scrubbed_lines)

def spacy_scrub(text: str) -> str:
    """Scrub names, orgs, locations using spaCy NER."""
    doc = nlp(text)
    scrubbed = text
    offset = 0

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE", "ORG", "LOC"]:
            start = ent.start_char + offset
            end = ent.end_char + offset
            replacement = "[REDACTED]"
            scrubbed = scrubbed[:start] + replacement + scrubbed[end:]
            offset += len(replacement) - (end - start)

    return scrubbed

def scrub_phi(text: str) -> str:
    """Main scrubbing pipeline."""
    text = regex_scrub(text)
    text = fuzzy_hospital_scrub(text)
    text = spacy_scrub(text)
    return text
