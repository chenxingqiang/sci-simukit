#!/usr/bin/env python3
import os
import json
import requests
import re
import argparse
from datetime import datetime
import time
from bs4 import BeautifulSoup

# API keys
SERPAPI_KEY = "ccb455bf2b78995c16bd150d248334ea8051214c1c76ce58f7582bc975638ee4"
CROSSREF_EMAIL = "your_email@example.com"  # For polite Crossref API usage

def search_google_scholar(query, num_results=10):
    """
    Search Google Scholar using SerpAPI

    Args:
        query (str): Search query
        num_results (int): Number of results to return

    Returns:
        list: Search results list with enhanced abstract information
    """
    base_url = "https://serpapi.com/search"

    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
        "as_ylo": 2018,  # 2018 and later, adjust as needed
        "as_yhi": 2025,  # Until 2024
        "hl": "en"
    }

    try:
        print(f"Searching for: {query}")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json()

        if "organic_results" in results:
            enhanced_results = []

            # Enhance results with more complete abstracts
            for i, paper in enumerate(results["organic_results"]):
                print(f"Processing result {i+1}/{len(results['organic_results'])}: {paper.get('title', 'No title')[:50]}...")

                # Try to get a more complete abstract
                enhanced_paper = enhance_paper_with_abstract(paper)
                enhanced_results.append(enhanced_paper)

                # Sleep briefly to avoid rate limiting
                time.sleep(1)

            return enhanced_results
        else:
            print(f"No results found for query: {query}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return []

def enhance_paper_with_abstract(paper):
    """
    Enhance paper with more complete abstract information

    Args:
        paper (dict): Original paper information from Google Scholar

    Returns:
        dict: Enhanced paper with more complete abstract
    """
    # First, check if we already have a snippet (partial abstract)
    snippet = paper.get("snippet", "")

    # If there's a link to the paper, try to get a more complete abstract
    link = paper.get("link", "")
    title = paper.get("title", "")

    # Extract author information
    authors = extract_authors_from_paper(paper)

    # Try to get a better abstract using Crossref API
    better_abstract = fetch_abstract_via_crossref(title, authors)

    # If Crossref didn't work and we have a link, try SerpAPI general search
    if not better_abstract and link:
        better_abstract = fetch_abstract_via_serpapi(title, link)

    # Update the paper with the best abstract we could find
    if better_abstract:
        # Keep the original snippet
        paper["original_snippet"] = snippet
        # Add the enhanced abstract
        paper["abstract"] = better_abstract
        # Also update the snippet field for backward compatibility
        paper["snippet"] = better_abstract
        print(f"  -> Enhanced abstract found ({len(better_abstract)} chars)")
    else:
        # If we couldn't find a better abstract, just use the original snippet
        paper["abstract"] = snippet
        print(f"  -> Using original snippet as abstract ({len(snippet)} chars)")

    return paper

def extract_authors_from_paper(paper):
    """Extract author information from paper data"""
    pub_info = paper.get("publication_info", {})
    authors = pub_info.get("authors", [])

    # If no authors in the authors field, try to extract from summary
    if not authors and "summary" in pub_info:
        summary = pub_info["summary"]
        # Try to extract authors from the summary (usually before the dash)
        parts = summary.split("-")
        if parts:
            potential_authors = parts[0].strip()
            # Split by common separators
            author_list = re.split(r',|\u2026', potential_authors)
            authors = [a.strip() for a in author_list if a.strip()]

    return authors

def fetch_abstract_via_crossref(title, authors):
    """
    Fetch abstract using Crossref API

    Args:
        title (str): Paper title
        authors (list): List of author names

    Returns:
        str or None: Abstract text if found, None otherwise
    """
    print(f"  -> Searching Crossref for: {title[:50]}...")

    # Prepare query - use first author's last name and title
    first_author = ""
    if authors:
        if isinstance(authors[0], dict) and "name" in authors[0]:
            first_author = authors[0]["name"]
        elif isinstance(authors[0], str):
            first_author = authors[0]

        # Extract last name if possible
        if " " in first_author:
            first_author = first_author.split()[-1]  # Get last name

    # Build query URL
    base_url = "https://api.crossref.org/works"
    query = f"{first_author} {title}"

    params = {
        "query": query,
        "rows": 3,  # Get top 3 results
        "mailto": CROSSREF_EMAIL  # Be polite
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if "message" in data and "items" in data["message"] and data["message"]["items"]:
            items = data["message"]["items"]

            # Find best match
            for item in items:
                if "abstract" in item:
                    # Clean up the abstract (remove HTML tags)
                    abstract = BeautifulSoup(item["abstract"], "html.parser").get_text()
                    print(f"  -> Found abstract via Crossref!")
                    return abstract

        print(f"  -> No abstract found via Crossref")
        return None

    except Exception as e:
        print(f"  -> Error fetching from Crossref: {e}")
        return None

def fetch_abstract_via_serpapi(title, url):
    """
    Try to fetch a more complete abstract using SerpAPI's Google search

    Args:
        title (str): Paper title
        url (str): URL to the paper

    Returns:
        str or None: Abstract text if found, None otherwise
    """
    print(f"  -> Searching for full abstract via SerpAPI for: {title[:50]}...")

    # If we have a URL, use it in the query for better results
    query = f"{title} abstract"
    if url:
        domain = url.split("//")[1].split("/")[0]  # Extract domain from URL
        query += f" site:{domain}"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3  # Limit to top 3 results
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "organic_results" in data and data["organic_results"]:
            # Look for abstract in snippet or description
            for result in data["organic_results"]:
                if "snippet" in result and len(result["snippet"]) > 200:  # Require longer snippet
                    print(f"  -> Found improved abstract via SerpAPI!")
                    return result["snippet"]

        print(f"  -> No improved abstract found via SerpAPI")
        return None

    except Exception as e:
        print(f"  -> Error fetching from SerpAPI: {e}")
        return None

def format_reference(paper):
    """Format paper information as a reference"""
    title = paper.get("title", "")

    # Extract authors
    authors = paper.get("publication_info", {}).get("authors", [])
    if not authors and "authors" in paper:
        authors = paper["authors"]

    author_names = []
    for author in authors:
        if isinstance(author, dict) and "name" in author:
            author_names.append(author["name"])
        elif isinstance(author, str):
            author_names.append(author)

    # Format author list
    if len(author_names) > 3:
        authors_str = f"{author_names[0]}, {author_names[1]}, et al."
    else:
        authors_str = ", ".join(author_names)

    # Extract year
    year = ""
    pub_info = paper.get("publication_info", {})
    if "summary" in pub_info:
        # Try to extract year from summary
        summary = pub_info["summary"]
        year_match = re.search(r'20\d{2}', summary)
        if year_match:
            year = year_match.group(0)

    if not year and "year" in paper:
        year = paper["year"]

    if not year:
        year = str(datetime.now().year)  # Default to current year

    # Extract journal/conference information
    venue = ""
    if "venue" in paper:
        venue = paper["venue"]
    elif "publisher" in pub_info:
        venue = pub_info["publisher"]
    elif "summary" in pub_info:
        venue = pub_info["summary"].split(",")[0]

    # Extract link
    link = paper.get("link", "")

    # Format reference
    reference = f"{authors_str} ({year}). {title}. "
    if venue:
        reference += f"{venue}. "
    if link:
        reference += f"Retrieved from {link}"

    return reference

def analyze_relevance(paper, keywords):
    """Analyze paper relevance based on keywords"""
    title = paper.get("title", "").lower()

    # Use enhanced abstract if available, otherwise use snippet
    abstract = paper.get("abstract", "").lower()
    if not abstract:
        abstract = paper.get("snippet", "").lower()

    score = 0
    matched_keywords = []

    for keyword, weight in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title:
            score += weight * 2  # Title match has double weight
            matched_keywords.append(keyword)
        elif keyword_lower in abstract:
            score += weight
            matched_keywords.append(keyword)

    return score, matched_keywords

def get_fullerene_strain_keywords():
    """Get keywords related to strain-tuned heteroatom-doped fullerene networks"""
    # Core fullerene keywords
    fullerene_keywords = [
        ("graphullerene", 20),
        ("fullerene network", 18),
        ("C60 network", 15),
        ("quasi-hexagonal phase", 15),
        ("qHP C60", 20),
        ("monolayer fullerene", 15),
        ("2D fullerene", 15),
        ("van der Waals fullerene", 12),
        ("vdW C60", 12),
        ("superatomic materials", 10),
    ]

    # Strain engineering keywords
    strain_keywords = [
        ("strain engineering", 18),
        ("mechanical strain", 15),
        ("biaxial strain", 15),
        ("tensile strain", 12),
        ("compressive strain", 12),
        ("strain-tunable", 15),
        ("strain modulation", 12),
        ("lattice deformation", 10),
        ("stress engineering", 10),
        ("mechanical deformation", 8),
    ]

    # Heteroatom doping keywords
    doping_keywords = [
        ("heteroatom doping", 18),
        ("boron doping", 15),
        ("nitrogen doping", 15),
        ("phosphorus doping", 15),
        ("B/N doping", 15),
        ("substitutional doping", 12),
        ("chemical doping", 10),
        ("band gap engineering", 15),
        ("electronic modification", 10),
        ("defect engineering", 8),
    ]

    # Electronic properties keywords
    electronic_keywords = [
        ("electron mobility", 18),
        ("quantum transport", 16),
        ("electron localization", 15),
        ("polaron formation", 15),
        ("electronic coupling", 15),
        ("charge transport", 12),
        ("carrier mobility", 12),
        ("band structure", 12),
        ("electronic band gap", 15),
        ("conductivity", 10),
        ("electronic properties", 12),
        ("transport properties", 12),
    ]

    # Computational methods keywords
    computational_keywords = [
        ("density functional theory", 15),
        ("DFT calculations", 15),
        ("first-principles", 12),
        ("ab initio", 10),
        ("CP2K", 8),
        ("Koopmans functional", 12),
        ("machine learning", 12),
        ("graph neural network", 10),
        ("GNN", 8),
        ("molecular dynamics", 10),
        ("MD simulation", 8),
    ]

    # Materials characterization keywords
    characterization_keywords = [
        ("inverse participation ratio", 12),
        ("IPR", 10),
        ("FCWD model", 10),
        ("Franck-Condon", 8),
        ("electron coupling", 12),
        ("reorganization energy", 10),
        ("thermal conductivity", 8),
        ("optical properties", 10),
        ("photoconductivity", 8),
    ]

    # Applications keywords
    application_keywords = [
        ("flexible electronics", 12),
        ("optoelectronic devices", 12),
        ("solar cells", 10),
        ("transistors", 8),
        ("sensors", 8),
        ("energy storage", 8),
        ("photovoltaics", 10),
        ("electronic devices", 8),
    ]

    # Combine all keywords and remove duplicates
    all_keywords = (fullerene_keywords + strain_keywords + doping_keywords +
                   electronic_keywords + computational_keywords +
                   characterization_keywords + application_keywords)

    unique_keywords = []
    seen_keywords = set()

    for keyword, weight in all_keywords:
        if keyword.lower() not in seen_keywords:
            unique_keywords.append((keyword, weight))
            seen_keywords.add(keyword.lower())

    return unique_keywords

def generate_search_queries():
    """Generate search queries for strain-tuned heteroatom-doped fullerene networks"""
    # Core research queries
    core_queries = [
        '"strain engineering" AND "fullerene" AND ("electronic properties" OR "band gap")',
        '"heteroatom doping" AND "fullerene" AND ("mobility" OR "transport")',
        '"graphullerene" AND ("strain" OR "mechanical deformation")',
        '"C60 network" AND "electron mobility" AND "density functional theory"',
        '"quasi-hexagonal phase" AND "C60" AND ("strain" OR "deformation")',
    ]

    # Strain-specific queries
    strain_queries = [
        '"biaxial strain" AND "2D materials" AND ("fullerene" OR "carbon")',
        '"strain-tunable" AND "electronic band gap" AND "carbon materials"',
        '"mechanical strain" AND "electron transport" AND "2D carbon"',
        '"tensile strain" AND "compressive strain" AND "electronic properties"',
        '"lattice deformation" AND "electronic structure" AND "fullerene"',
    ]

    # Doping-specific queries
    doping_queries = [
        '"boron doping" AND "nitrogen doping" AND "fullerene"',
        '"heteroatom substitution" AND "C60" AND "electronic properties"',
        '"B/N doping" AND "band gap engineering" AND "carbon materials"',
        '"phosphorus doping" AND "fullerene" AND "transport properties"',
        '"chemical doping" AND "strain" AND "2D materials"',
    ]

    # Transport and electronic properties queries
    transport_queries = [
        '"electron mobility" AND "polaron" AND "fullerene"',
        '"quantum transport" AND "electron localization" AND "carbon"',
        '"charge transport" AND "electronic coupling" AND "fullerene network"',
        '"carrier mobility" AND "strain" AND "2D carbon materials"',
        '"electronic band structure" AND "strain engineering" AND "fullerene"',
    ]

    # Computational methods queries
    computational_queries = [
        '"density functional theory" AND "fullerene" AND "strain"',
        '"DFT calculations" AND "heteroatom doping" AND "carbon materials"',
        '"first-principles" AND "electron transport" AND "fullerene"',
        '"machine learning" AND "materials design" AND ("fullerene" OR "carbon")',
        '"CP2K" AND "electronic structure" AND "2D materials"',
    ]

    # Applications queries
    application_queries = [
        '"flexible electronics" AND "strain-responsive" AND "carbon materials"',
        '"optoelectronic devices" AND "tunable band gap" AND "fullerene"',
        '"strain sensors" AND "electronic readout" AND "2D materials"',
        '"photovoltaic" AND "strain-tunable" AND "carbon"',
        '"electronic devices" AND "mechanical deformation" AND "fullerene"',
    ]

    # Combined advanced queries
    advanced_queries = [
        '"strain engineering" AND "heteroatom doping" AND "fullerene" AND "electronic properties"',
        '"graphullerene" AND "boron" AND "nitrogen" AND "strain"',
        '"C60 network" AND "mechanical deformation" AND "electron mobility"',
        '"2D fullerene" AND "band gap tuning" AND "chemical doping"',
        '"quasi-hexagonal phase" AND "electronic transport" AND "strain modulation"',
    ]

    # Combine all queries
    all_queries = (core_queries + strain_queries + doping_queries +
                  transport_queries + computational_queries +
                  application_queries + advanced_queries)

    return all_queries

def generate_detailed_markdown(analyzed_papers, keywords, search_queries, timestamp):
    """Generate detailed Markdown report of search results"""
    markdown = f"# Google Scholar Search Results for Strain-Tuned Heteroatom-Doped Fullerene Networks\n\n"

    # Add search information
    markdown += f"## Search Information\n\n"
    markdown += f"**Date:** {timestamp}\n\n"
    markdown += f"**Number of Papers:** {len(analyzed_papers)}\n\n"
    markdown += f"**Research Focus:** Strain engineering and heteroatom doping in graphullerene networks\n\n"
    markdown += f"**Search Queries:**\n\n"
    for query in search_queries:
        markdown += f"- {query}\n"

    markdown += f"\n**Keywords and Weights:**\n\n"
    for keyword, weight in keywords:
        markdown += f"- {keyword}: {weight}\n"

    # Add search results
    markdown += f"\n## Top Relevant Papers\n\n"

    for i, (paper, score, matched_keywords) in enumerate(analyzed_papers, 1):
        reference = format_reference(paper)
        markdown += f"### {i}. {paper.get('title', 'No Title')}\n\n"
        markdown += f"**Reference:** {reference}\n\n"
        markdown += f"**Relevance Score:** {score}\n\n"
        markdown += f"**Matched Keywords:** {', '.join(matched_keywords)}\n\n"

        # Use enhanced abstract if available
        abstract = paper.get("abstract", paper.get("snippet", "No abstract available"))
        markdown += f"**Abstract:** {abstract}\n\n"

        # Add link
        if "link" in paper:
            markdown += f"**Link:** [{paper['link']}]({paper['link']})\n\n"

        # Add citation information
        if "cited_by" in paper and "value" in paper["cited_by"]:
            markdown += f"**Cited by:** {paper['cited_by']['value']} papers\n\n"

        markdown += f"---\n\n"

    return markdown

def generate_reference_markdown(analyzed_papers, timestamp):
    """Generate reference list in Markdown format"""
    markdown = f"# References for Strain-Tuned Heteroatom-Doped Fullerene Networks\n\n"
    markdown += f"**Generated on:** {timestamp}\n\n"

    for i, (paper, _, _) in enumerate(analyzed_papers, 1):
        reference = format_reference(paper)
        markdown += f"{i}. {reference}\n\n"

    return markdown

def generate_categorized_references(analyzed_papers, timestamp):
    """Generate categorized references"""
    # Define categories based on our research focus
    categories = {
        "富勒烯基础研究": ["graphullerene", "fullerene network", "c60 network", "quasi-hexagonal phase",
                      "qhp c60", "monolayer fullerene", "2d fullerene", "superatomic materials"],

        "应变工程": ["strain engineering", "mechanical strain", "biaxial strain", "tensile strain",
                  "compressive strain", "strain-tunable", "strain modulation", "lattice deformation"],

        "杂原子掺杂": ["heteroatom doping", "boron doping", "nitrogen doping", "phosphorus doping",
                    "b/n doping", "substitutional doping", "chemical doping", "band gap engineering"],

        "电子传输性质": ["electron mobility", "quantum transport", "electron localization",
                     "polaron formation", "electronic coupling", "charge transport", "carrier mobility"],

        "计算方法": ["density functional theory", "dft calculations", "first-principles", "ab initio",
                  "cp2k", "koopmans functional", "machine learning", "molecular dynamics"],

        "器件应用": ["flexible electronics", "optoelectronic devices", "solar cells", "transistors",
                  "sensors", "energy storage", "photovoltaics", "electronic devices"],

        "表征方法": ["inverse participation ratio", "ipr", "fcwd model", "franck-condon",
                  "electron coupling", "reorganization energy", "optical properties"]
    }

    # Initialize categorized papers
    categorized_papers = {category: [] for category in categories}

    # Categorize papers
    for paper, score, keywords in analyzed_papers:
        title = paper.get("title", "").lower()

        # Use enhanced abstract if available
        abstract = paper.get("abstract", "").lower()
        if not abstract:
            abstract = paper.get("snippet", "").lower()

        content = title + " " + abstract

        for category, category_keywords in categories.items():
            if any(kw in content for kw in category_keywords):
                categorized_papers[category].append((paper, score, keywords))

    # Generate Markdown
    markdown = f"# Categorized References for Strain-Tuned Heteroatom-Doped Fullerene Networks\n\n"
    markdown += f"**Generated on:** {timestamp}\n\n"

    for category, papers in categorized_papers.items():
        if papers:
            markdown += f"## {category}\n\n"
            for i, (paper, score, _) in enumerate(sorted(papers, key=lambda x: x[1], reverse=True), 1):
                reference = format_reference(paper)
                markdown += f"{i}. {reference}\n\n"

    return markdown

def save_to_markdown(content, filename):
    """Save content to a Markdown file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved to {filename}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Search for academic papers related to strain-tuned heteroatom-doped fullerene networks")
    parser.add_argument("--num_papers", type=int, default=50, help="Number of papers to retrieve (default: 50)")
    args = parser.parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a timestamped directory
    timestamp_dir = f"fullerene_strain_search_{timestamp}"
    os.makedirs(timestamp_dir, exist_ok=True)

    # Get keywords
    print("Extracting fullerene strain engineering keywords...")
    keywords = get_fullerene_strain_keywords()

    # Generate search queries
    search_queries = generate_search_queries()

    # Calculate papers per query
    papers_per_query = max(3, args.num_papers // len(search_queries))

    all_papers = []

    for query in search_queries:
        print(f"\nSearching for: {query}")
        results = search_google_scholar(query, num_results=papers_per_query)
        all_papers.extend(results)
        time.sleep(2)  # Avoid API rate limits

    # Remove duplicates
    unique_papers = []
    seen_titles = set()

    for paper in all_papers:
        title = paper.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_papers.append(paper)

    # Analyze relevance and sort
    analyzed_papers = []
    for paper in unique_papers:
        relevance_score, matched_keywords = analyze_relevance(paper, keywords)
        if relevance_score > 0:  # Only keep relevant papers
            analyzed_papers.append((paper, relevance_score, matched_keywords))

    # Sort by relevance
    analyzed_papers.sort(key=lambda x: x[1], reverse=True)

    # Limit paper count
    analyzed_papers = analyzed_papers[:args.num_papers]

    # Output results
    print(f"\n=== Found {len(analyzed_papers)} relevant academic papers ===\n")

    for i, (paper, score, matched_keywords) in enumerate(analyzed_papers[:10], 1):
        reference = format_reference(paper)
        print(f"{i}. {reference}")
        print(f"   Relevance score: {score}")
        print(f"   Matched keywords: {', '.join(matched_keywords)}")

        # Print first 200 chars of abstract
        abstract = paper.get("abstract", paper.get("snippet", "No abstract"))
        print(f"   Abstract: {abstract[:200]}...\n")

    if len(analyzed_papers) > 10:
        print(f"... and {len(analyzed_papers) - 10} more papers (see generated files)\n")

    # Generate filenames
    results_filename = "fullerene_strain_search_results.md"
    references_filename = "fullerene_strain_references.md"
    categorized_filename = "fullerene_strain_categorized_references.md"
    data_filename = "fullerene_strain_search_data.json"

    # Generate Markdown files
    detailed_markdown = generate_detailed_markdown(analyzed_papers, keywords, search_queries, formatted_timestamp)
    reference_markdown = generate_reference_markdown(analyzed_papers, formatted_timestamp)
    categorized_markdown = generate_categorized_references(analyzed_papers, formatted_timestamp)

    # Save files in the timestamped directory
    save_to_markdown(detailed_markdown, os.path.join(timestamp_dir, results_filename))
    save_to_markdown(reference_markdown, os.path.join(timestamp_dir, references_filename))
    save_to_markdown(categorized_markdown, os.path.join(timestamp_dir, categorized_filename))

    # Save raw data for further analysis
    with open(os.path.join(timestamp_dir, data_filename), "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": formatted_timestamp,
            "search_queries": search_queries,
            "keywords": keywords,
            "papers": [p[0] for p in analyzed_papers]
        }, f, indent=2)
    print(f"Saved data in folder: {timestamp_dir}")

    # Save latest versions without timestamp in the main directory
    save_to_markdown(detailed_markdown, "fullerene_strain_search_results_latest.md")
    save_to_markdown(reference_markdown, "fullerene_strain_references_latest.md")
    save_to_markdown(categorized_markdown, "fullerene_strain_categorized_references_latest.md")
    with open("fullerene_strain_search_data_latest.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": formatted_timestamp,
            "search_queries": search_queries,
            "keywords": keywords,
            "papers": [p[0] for p in analyzed_papers]
        }, f, indent=2)

if __name__ == "__main__":
    main()
