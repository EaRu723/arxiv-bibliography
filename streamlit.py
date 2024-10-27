import streamlit as st
from collections import namedtuple
import psycopg2
import json
from collections import namedtuple

# Set up the Streamlit page
st.set_page_config(page_title="W3asy Bib", page_icon="📚")
st.title("W3asy Bib")
st.subheader("A Tokenized Bibliography for the Web")

# Create input field for ArXiv URL
your_url = st.text_input("Enter URL:", "https://arxiv.org/abs/2008.11149")

# Create a button to trigger the scraping
if st.button("Let's Go"):
    try:
        ArxivPaper = namedtuple("ArxivPaper", ["Title", "Authors", "Abstract", "DOI"])
        
        # Database connection
        conn = psycopg2.connect("dbname='you' host='lsd.so'")
        
        with conn.cursor() as curs:
            curs.execute(f"""SELECT
            h1.title.mathjax AS Title
            , div.authors AS Authors
            , blockquote.abstract.mathjax AS Abstract
            , a#arxiv-doi-link AS DOI
            FROM
                {your_url}
            GROUP BY
                div#content-inner;""")
            rows = curs.fetchall()
            papers = []
            for row in rows:
                arxiv_paper = ArxivPaper(*row)
                
                # Clean up the values
                title = arxiv_paper.Title.replace("Title:", "").strip()
                authors = arxiv_paper.Authors.replace("Authors:", "").strip()
                abstract = arxiv_paper.Abstract.strip()
                # Remove extra whitespace and newlines from abstract
                abstract = " ".join(abstract.split())
                # Remove "Abstract:" if present
                if abstract.startswith("Abstract:"):
                    abstract = abstract[9:].strip()
                
                paper_dict = {
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "doi": arxiv_paper.DOI,
                    "url": your_url,
                }
                papers.append(paper_dict)
            
            # Convert to JSON
            json_output = json.dumps(papers, indent=2)
            
            # Display results in Streamlit
            st.subheader("Results")
            
            # Display each paper's details
            for paper in papers:
                st.markdown("### 📄 " + paper['title'])
                st.markdown("**Authors:** ")
                st.markdown(paper['authors'])
                st.markdown("**Abstract:**")
                st.markdown(paper['abstract'])
                st.markdown("**DOI:** " + paper['doi'])
                st.markdown("**URL:** " + paper['url'])
                st.markdown("---")
            
            # Add download button for JSON
            st.download_button(
                label="Download JSON",
                data=json_output,
                file_name="papers.json",
                mime="application/json"
            )
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")