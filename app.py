from collections import namedtuple
import psycopg2
import json
from collections import namedtuple

# conn = psycopg2.connect("dbname='you' host='lsd.so'")
# with conn.cursor() as curs:
#   curs.execute("""
#     SELECT
#     a[title="Abstract"]@href AS abstract_link
#     FROM
#     https://arxiv.org/list/physics/2024-02
#     GROUP BY
#   dt;""")
#   row = curs.fetchall()
#   print(row)


ArxivPaper = namedtuple("ArxivPaper", ["Title", "Authors", "Abstract", "DOI"])

conn = psycopg2.connect("dbname='you' host='lsd.so'")
your_url = "https://arxiv.org/abs/2008.11149"
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
        paper_dict = {
            "title": arxiv_paper.Title,
            "authors": arxiv_paper.Authors,
            "abstract": arxiv_paper.Abstract,
            "doi": arxiv_paper.DOI
        }
        papers.append(paper_dict)
    
    # Convert to JSON and print
    json_output = json.dumps(papers, indent=2)
    print(json_output)

    # Optionally, save to file
    with open('papers.json', 'w') as f:
        f.write(json_output)