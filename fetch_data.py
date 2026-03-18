import json, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open("/Users/adelaideguo/code/claude/aswtools/paperindex/.trae/skills/citation-linker/extracted_queries.json") as f:
    queries = json.load(f)

results = []
for q in queries:
    url = q["openalex_url"]
    print(f"Fetching: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Trae-Skill-Citation-Linker/1.0 (mailto:test@example.com)"})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            # Convert OpenAlex response to the format expected by citation_linker.py
            papers = []
            for w in data.get('results', []):
                authors = []
                for a in w.get('authorships', []):
                    an = a.get('author', {})
                    display = a.get('display_name', '')
                    if display:
                        authors.append(display)
                    elif an.get('display_name'):
                        authors.append(an['display_name'])

                locations = w.get('locations', [])
                doi = w.get('doi', '')
                url_paper = doi
                pdf_url = ''
                
                # Try to find a direct PDF URL first, then fallback to landing page
                for loc in locations:
                    if loc.get('pdf_url'):
                        pdf_url = loc.get('pdf_url')
                        url_paper = pdf_url
                        break
                
                if not pdf_url:
                    for loc in locations:
                        if loc.get('landing_page_url'):
                            url_paper = loc.get('landing_page_url')
                            break
                
                open_access = w.get('open_access', {})
                is_oa = open_access.get('is_oa', False)
                oa_url = open_access.get('oa_url', '')
                
                if oa_url and not pdf_url:
                    url_paper = oa_url
                    pdf_url = oa_url

                published = ''
                date = w.get('publication_date', '')
                if not date and w.get('publication_year'):
                    published = str(w['publication_year'])
                elif date:
                    published = date[:10] if len(date) >= 10 else date

                primary_loc = w.get('primary_location', {})
                source = primary_loc.get('source', {}) or {}
                journal = source.get('display_name', '')

                papers.append({
                    'id': w.get('id', '').split('/')[-1] if w.get('id') else '',
                    'title': w.get('title', '') or '',
                    'authors': authors[:8],
                    'published': published,
                    'year': w.get('publication_year', ''),
                    'journal': journal,
                    'doi': doi,
                    'url': url_paper or doi,
                    'pdf_url': pdf_url,
                    'is_oa': is_oa,
                    'abstract': w.get('abstract', '') or '',
                    'cited_by': w.get('cited_by_count', 0),
                    'topics': [t.get('display_name', '') for t in w.get('topics', [])[:4]],
                })
                
            results.append({
                "cite_key": q["cite_key"],
                "papers": papers
            })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        results.append({
            "cite_key": q["cite_key"],
            "papers": []
        })

with open("/Users/adelaideguo/code/claude/aswtools/paperindex/.trae/skills/citation-linker/results.json", "w") as f:
    json.dump(results, f, ensure_ascii=False)
