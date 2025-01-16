from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import streamlit as st

# Function to scrape faculty name and tab content
def scrape_faculty_and_tabs(url, tab_hrefs):
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(10)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        faculty_name = soup.find('h3', class_='facDet1')
        faculty_name = faculty_name.text.strip() if faculty_name else "Faculty name not found"

        tab_results = []
        for tab_href in tab_hrefs:
            tab_link = soup.find('a', href=tab_href)
            if tab_link:
                tab_name = tab_link.text.strip()
                tab_id = tab_href.lstrip('#')
                tab_content = soup.find('div', id=tab_id)
                tab_content_text = tab_content.get_text(strip=True) if tab_content else "No content found for this tab."
            else:
                tab_name = "Tab not found."
                tab_content_text = "Tab content not found."
            
            tab_results.append((tab_name, tab_content_text))

        driver.quit()
        return faculty_name, tab_results
    except Exception as e:
        return "Error", [("Error", f"Error scraping URL {url}: {str(e)}")]

# Streamlit UI
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        body { background-color: #F5F5F5; color: #37474F; animation: fadeIn 1s ease-in-out; }
        .title { font-size: 36px; color: #00897B; text-align: center; }
        .subheader { font-size: 18px; text-align: center; color: #37474F; }
    </style>
    <div class="title">Faculty Assignment Portal</div>
    """,
    unsafe_allow_html=True
)

faculty_urls = st.text_area(
    "Enter Faculty URLs (one per line):",
    "https://example.com/faculty1\nhttps://example.com/faculty2"
)

tab_hrefs_input = st.text_area(
    "Enter tab hrefs (one per line):",
    "#tab_default_4\n#tab_default_601"
)

if st.button("Scrape Content"):
    urls = [url.strip() for url in faculty_urls.splitlines() if url.strip()]
    tab_hrefs = [tab.strip() for tab in tab_hrefs_input.splitlines() if tab.strip()]
    
    if urls and tab_hrefs:
        with st.spinner("Scraping data..."):
            all_results = []
            for url in urls:
                faculty_name, tab_results = scrape_faculty_and_tabs(url, tab_hrefs)
                all_results.append((url, faculty_name, tab_results))
        
        st.subheader("Scraping Results")
        for url, faculty_name, tab_results in all_results:
            st.write(f"**URL:** {url}")
            st.write(f"**Faculty Name:** {faculty_name}")
            
            # Loop through tab results and show buttons for each
            for tab_name, tab_content in tab_results:
                with st.expander(f"View Data - {tab_name}"):
                    st.text_area(f"Content - {tab_name}", tab_content, height=200)

            st.markdown("---")
    else:
        st.error("Please enter at least one URL and one tab href.")
