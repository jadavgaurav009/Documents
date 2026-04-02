import streamlit as st
import pdfplumber
import json
import tempfile

st.set_page_config(layout="wide")
st.title("🔥 ACORD PDF Extractor (100% Position-Based)")

# ------------------------------
# FIELD LABELS
# ------------------------------
FIELD_LABELS = {
    "APPLICANT_NAME": ["APPLICANT'S NAME"],
    "DOB": ["DATE OF BIRTH"],
    "EMAIL": ["E-MAIL", "PRIMARY E-MAIL ADDRESS"],
    "PHONE": ["PHONE"],
    "ADDRESS": ["MAILING ADDRESS", "ADDRESS"],
    "AGENCY_NAME": ["AGENCY"],
    "POLICY_NUMBER": ["POLICY NUMBER"],
    "EFFECTIVE_DATE": ["EFFECTIVE DATE"],
    "EXPIRATION_DATE": ["EXPIRATION DATE"]
}

# ------------------------------
# HELPERS
# ------------------------------
def find_label(words, label_keywords):
    for w in words:
        for key in label_keywords:
            if key.lower() in w['text'].lower():
                return w
    return None


def extract_value(words, label_word):
    lx0, lx1 = label_word['x0'], label_word['x1']
    top = label_word['top']

    same_line = []
    below_line = []

    for w in words:
        if abs(w['top'] - top) < 5 and w['x0'] > lx1:
            same_line.append(w)

        if (w['top'] > top and w['top'] < top + 40 and
            abs(w['x0'] - lx0) < 200):
            below_line.append(w)

    if same_line:
        return " ".join([w['text'] for w in same_line])

    if below_line:
        return " ".join([w['text'] for w in below_line])

    return ""


def extract_fields(pdf_path):
    result = {}

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()

        for field, labels in FIELD_LABELS.items():
            label_word = find_label(words, labels)

            if label_word:
                result[field] = extract_value(words, label_word)
            else:
                result[field] = ""

    return result


def extract_tables(pdf_path):
    tables_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables_data.append(table)

    return tables_data


# ------------------------------
# UI INPUT
# ------------------------------
uploaded_file = st.file_uploader("📂 Upload ACORD PDF", type=["pdf"])
file_path = st.text_input("OR Enter PDF Path")

pdf_source = None

if uploaded_file:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(uploaded_file.read())
    pdf_source = temp_file.name

elif file_path:
    pdf_source = file_path


# ------------------------------
# PROCESS
# ------------------------------
if pdf_source:
    st.success("Processing PDF...")

    fields = extract_fields(pdf_source)
    tables = extract_tables(pdf_source)

    result = {
        "fields": fields,
        "tables": tables
    }

    # Show JSON
    st.subheader("📊 Extracted Data")
    st.json(result)

    # Download button
    json_str = json.dumps(result, indent=4)
    st.download_button(
        label="⬇️ Download JSON",
        data=json_str,
        file_name="acord_output.json",
        mime="application/json"
    )