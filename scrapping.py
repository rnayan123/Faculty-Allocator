import streamlit as st
import pandas as pd
import re
import nltk
from selenium import webdriver
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data
nltk.download("stopwords")
nltk.download("wordnet")

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Predefined list of subjects categorized by semester
subjects_by_semester = {
    "Sem 1": ["Mathematical Foundation for Computer Science","Problem Solving Using C ","Research Methodology ","Computer Organization and Design","Advanced Database Technologies","Python Programming ","WebDevelopment ","React"],
    "Sem 2": ["Java", "Operating Systems", "Database Management"],
    "Sem 3": ["Machine Learning", "Deep Learning", "Artificial Intelligence","IOT"],
    "All": []
}

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return " ".join(words)

# Function to check for matching expertise
def extract_expertise(row_text, subjects):
    matched_subjects = [subject for subject in subjects if subject.lower() in row_text.lower()]
    return ", ".join(matched_subjects) if matched_subjects else None

# Function to scrape faculty name and tab content
def scrape_faculty_and_tabs(url, tab_hrefs):
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(10)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        faculty_name = soup.find("h3", class_="facDet1")
        faculty_name = faculty_name.text.strip() if faculty_name else "Faculty name not found"

        tab_results = []
        for tab_href in tab_hrefs:
            tab_link = soup.find("a", href=tab_href)
            if tab_link:
                tab_name = tab_link.text.strip()
                tab_id = tab_href.lstrip("#")
                tab_content = soup.find("div", id=tab_id)
                if tab_content:
                    tab_text = preprocess_text(tab_content.get_text(strip=True))
                    tab_results.append({"Tab Name": tab_name, "Tab Data": tab_text})
                else:
                    tab_results.append({"Tab Name": tab_name, "Tab Data": "No content found"})
            else:
                tab_results.append({"Tab Name": "Tab not found", "Tab Data": "Tab content not found"})

        driver.quit()
        return faculty_name, tab_results
    except Exception as e:
        return "Error", [{"Tab Name": "Error", "Tab Data": f"Error scraping URL {url}: {str(e)}"}]

# Streamlit UI
st.title("Subject Allocation & Expertise Portal")

faculty_urls = st.text_area("Enter Faculty URLs (one per line):", "https://example.com/faculty1\nhttps://example.com/faculty2")

tab_hrefs_input = st.text_area("Enter tab hrefs (one per line):", "#tab_default_4\n#tab_default_601")

# Dropdown for semester selection
selected_semester = st.selectbox("Select Semester", list(subjects_by_semester.keys()))

if st.button("Scrape and Preprocess Data"):
    urls = [url.strip() for url in faculty_urls.splitlines() if url.strip()]
    tab_hrefs = [tab.strip() for tab in tab_hrefs_input.splitlines() if tab.strip()]
    subjects_list = subjects_by_semester[selected_semester] if selected_semester != "All" else sum(subjects_by_semester.values(), [])
    
    if urls and tab_hrefs:
        with st.spinner("Scraping data..."):
            all_data = []
            expertise_data = []

            for url in urls:
                faculty_name, tab_results = scrape_faculty_and_tabs(url, tab_hrefs)
                faculty_expertise = set()

                for tab_result in tab_results:
                    matched_expertise = extract_expertise(tab_result["Tab Data"], subjects_list)
                    if matched_expertise:
                        faculty_expertise.update(matched_expertise.split(", "))

                    all_data.append({
                        "URL": url,
                        "Faculty Name": faculty_name,
                        "Tab Name": tab_result["Tab Name"],
                        "Matched Expertise": matched_expertise or "No relevant subject found"
                    })

                expertise_data.append({
                    "Faculty Name": faculty_name,
                    "Matched Expertise": ", ".join(faculty_expertise) if faculty_expertise else "No relevant expertise found"
                })

            raw_data_df = pd.DataFrame(all_data)
            expertise_df = pd.DataFrame(expertise_data)

            st.subheader("Scraped Raw Tab Data")
            st.dataframe(raw_data_df)

            st.subheader("Faculty Expertise")
            st.dataframe(expertise_df)

            raw_data_csv = "faculty_raw_data.csv"
            expertise_csv = "faculty_expertise.csv"
            raw_data_df.to_csv(raw_data_csv, index=False)
            expertise_df.to_csv(expertise_csv, index=False)

            st.success("Data scraped and processed successfully.")
            st.download_button("Download Raw Tab Data CSV", raw_data_df.to_csv(index=False), file_name=raw_data_csv, mime="text/csv")
            st.download_button("Download Expertise Data CSV", expertise_df.to_csv(index=False), file_name=expertise_csv, mime="text/csv")
    else:
        st.error("Please enter at least one URL and one tab href.")
