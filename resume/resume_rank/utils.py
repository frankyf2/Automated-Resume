import fitz
import spacy
import re
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file):
    try:
        with fitz.open(file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        # Clean up special characters
        text = text.replace("ï¼", ",").replace("â€“", "-").replace("\n", " ").replace("\t", " ")
        text = re.sub(r"\s+", " ", text).strip()

        # Extract sections
        sections = {
            "education": re.findall(r"(education|academic|qualification|degree)(.*?)(experience|work|skills|projects|$)", text, re.DOTALL | re.IGNORECASE),
            "experience": re.findall(r"(experience|work)(.*?)(education|skills|projects|$)", text, re.DOTALL | re.IGNORECASE),
            "skills": re.findall(r"(skills|technologies|tools|competencies)(.*?)(education|experience|projects|$)", text, re.DOTALL | re.IGNORECASE),
            "projects": re.findall(r"(projects|portfolio|works)(.*?)(education|experience|skills|$)", text, re.DOTALL | re.IGNORECASE),
        }

        # Extract and clean each section
        extracted_data = {}
        all_keywords = set()

        for section, matches in sections.items():
            content = " ".join([match[1].strip() for match in matches])
            # Use spaCy to further process
            doc = nlp(content.lower())
            keywords = set()

            # Preserve multi-word phrases
            for chunk in doc.noun_chunks:
                keywords.add(chunk.text.replace(" ", "_"))
            
            # Add individual words as fallback
            for token in doc:
                if not token.is_stop and token.is_alpha:
                    keywords.add(token.lemma_)

            # Combine keywords and remove duplicates
            extracted_data[section] = ", ".join(keywords)
            all_keywords.update(keywords)

        # Prepare final output
        extracted_data["keywords"] = ", ".join(all_keywords)
        return extracted_data

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return {}

# Predefined multi-word technical terms and phrases
multi_word_terms = [
    "full stack developer", "machine learning", "data science", "artificial intelligence",
    "computer science", "web development", "version control", "rest apis", "api integration",
    "project management", "software engineering", "natural language processing",
]

# Initialize the PhraseMatcher
phrase_matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp(term) for term in multi_word_terms]
phrase_matcher.add("TECH_TERMS", patterns)

def j_extract_keywords(title, required_skills, education_level, course, description):
    # Prepare the full text for analysis (excluding education)
    full_text = f"{title} {required_skills} {description}".lower()

    # Process the text with spaCy
    doc = nlp(full_text)
    keywords = set()

    # Extract multi-word terms using PhraseMatcher
    matches = phrase_matcher(doc)
    for match_id, start, end in matches:
        phrase = "_".join(doc[start:end].text.split())
        keywords.add(phrase)

    # Add meaningful single words
    for token in doc:
        if not token.is_stop and token.is_alpha and len(token.text) > 2:
            keywords.add(token.lemma_)
    
    # Remove overly generic terms
    common_ignore_words = {"job", "title", "experience", "years", "skill", "education", "level", 
                           "required", "description", "company", "position", "developer", 
                           "skilled", "like", "look", "system"}
    keywords = {kw for kw in keywords if kw not in common_ignore_words}

    # Add education level and course as separate phrases
    if education_level:
        keywords.add("_".join(education_level.lower().split()))
    if course:
        keywords.add("_".join(course.lower().split()))

    # Deduplicate and sort keywords
    return ", ".join(sorted(keywords))

