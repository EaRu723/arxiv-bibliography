import streamlit as st
from collections import namedtuple
import psycopg2
import json
from collections import namedtuple
from datetime import datetime
import hashlib
import socket

# Set up the Streamlit page
st.set_page_config(page_title="Arxiv Bibliography", page_icon="📚")
st.title("Arxiv Bibliography")
st.subheader("Enter an Arxiv URL to get Title, Authors, Abstract, and DOI")

# Create input field for ArXiv URL
your_url = st.text_input("Enter URL:", "https://arxiv.org/abs/2403.00268")

# Create a button to trigger the scraping
if st.button("Let's Go"):
    try:
        # Get user's IP address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        current_time = datetime.now().isoformat()
        
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
                # Generate token for each paper
                token_input = f"{ip_address}{paper['doi']}{current_time}"
                paper_token = hashlib.sha256(token_input.encode()).hexdigest()
                paper['token'] = paper_token
                
                st.markdown("### 📄 " + paper['title'])
                st.markdown("**Authors:** ")
                st.markdown(paper['authors'])
                st.markdown("**Abstract:**")
                st.markdown(paper['abstract'])
                st.markdown("**DOI:** " + paper['doi'])
                st.markdown("**URL:** " + paper['url'])
                st.markdown("**Token:** " + paper['token'])
                st.markdown("---")
            
            # Add download button for JSON
            st.download_button(
                label="Download JSON",
                data=json_output,
                file_name="papers.json",
                mime="application/json"
            )
            
            # Inside your "Let's Go" button logic
            paper_access_record = {
                "ip_address": ip_address,
                "paper_doi": paper['doi'],
                "access_time": current_time,
                "token": paper_token
            }
            
            # Display access record
            st.subheader("📋 Access Record")
            st.json(paper_access_record)
            
            # You could store this in a database for later verification
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")