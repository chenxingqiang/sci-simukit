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
        "as_yhi": 2024,  # Until 2024
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

def get_cdk46_cancer_keywords():
    """Get keywords related to CDK4/6 inhibitors and cancer"""
    # Clinical keywords
    clinical_keywords = [
        ("CDK4/6 expression", 15),
        ("gastroesophageal junction adenocarcinoma", 15),
        ("immunohistochemistry", 10),
        ("IHC", 10),
        ("Ki-67", 12),
        ("clinical prognosis", 12),
        ("GEJ adenocarcinoma", 15),
        ("esophagogastric junction cancer", 15),
        ("prognostic model", 10),
        ("public database", 8),
    ]
    
    # Cellular keywords
    cellular_keywords = [
        ("CDK4/6 inhibition", 15),
        ("radiotherapy", 15),
        ("in vitro", 10),
        ("Palbociclib", 15),
        ("Abemaciclib", 15),
        ("Ribociclib", 15),
        ("radiosensitivity", 13),
        ("MTT assay", 8),
        ("clonogenic assay", 8),
        ("cell cycle arrest", 12),
        ("apoptosis", 12),
        ("DNA damage response", 10),
        ("γ-H2AX", 10),
        ("Single-cell RNA sequencing", 8),
        ("CO-IP", 7),
        ("western blot", 7),
        ("reporter assay", 7),
        ("signaling pathway", 10),
    ]
    
    # Animal keywords
    animal_keywords = [
        ("CDK4/6 inhibitor", 15),
        ("xenograft model", 13),
        ("mouse tumor model", 13),
        ("tumor regression", 12),
        ("in vivo", 10),
        ("thermal imaging", 8),
        ("treatment response", 10),
        ("tumor growth", 12),
        ("nude mice", 10),
        ("PK/PD", 8),
        ("pharmacokinetics", 8),
    ]
    
    # Combine all keywords and remove duplicates
    all_keywords = clinical_keywords + cellular_keywords + animal_keywords
    unique_keywords = []
    seen_keywords = set()
    
    for keyword, weight in all_keywords:
        if keyword.lower() not in seen_keywords:
            unique_keywords.append((keyword, weight))
            seen_keywords.add(keyword.lower())
    
    return unique_keywords

def generate_search_queries():
    """Generate search queries for CDK4/6 inhibitors and cancer"""
    # Clinical queries
    clinical_queries = [
        '"CDK4/6 expression" AND "gastroesophageal junction adenocarcinoma" AND ("immunohistochemistry" OR "IHC")',
        '"CDK4/6" AND "Ki-67" AND "correlation" AND "gastroesophageal cancer"',
        '"CDK4/6 expression" AND "clinical prognosis" AND ("GEJ adenocarcinoma" OR "esophagogastric junction cancer")',
        '"prognostic model" AND "gastroesophageal junction adenocarcinoma" AND "public database" AND "CDK4/6"'
    ]
    
    # Cellular queries
    cellular_queries = [
        '"CDK4/6 inhibition" AND "radiotherapy" AND "gastroesophageal junction adenocarcinoma" AND "in vitro"',
        '"Palbociclib" OR "Abemaciclib" AND "radiosensitivity" AND ("MTT assay" OR "clonogenic assay")',
        '"CDK4/6 inhibitor" AND "cell cycle arrest" AND "apoptosis" AND "radiotherapy"',
        '"CDK4/6 inhibition" AND "DNA damage response" AND "γ-H2AX"',
        '"Single-cell RNA sequencing" AND "CDK4/6 inhibition" AND "radiotherapy"',
        '"CO-IP" OR "western blot" OR "reporter assay" AND "CDK4/6" AND "signaling pathway"'
    ]
    
    # Animal queries
    animal_queries = [
        '"CDK4/6 inhibitor" AND "xenograft model" AND "gastroesophageal junction adenocarcinoma"',
        '"Palbociclib" OR "Abemaciclib" AND "radiotherapy" AND "mouse tumor model"',
        '"CDK4/6" AND "tumor regression" AND "in vivo" AND "radiotherapy"',
        '"thermal imaging" AND "xenograft model" AND "treatment response"',
        '"CDK4/6 inhibition" AND "tumor growth" AND "nude mice"'
    ]
    
    # Combined queries
    combined_queries = [
        '"CDK4/6 inhibitor" AND "gastroesophageal cancer" AND "radiotherapy"',
        '"Palbociclib" AND "esophagogastric junction" AND "cancer treatment"',
        '"Abemaciclib" AND "gastroesophageal junction" AND "combined therapy"',
        '"Ribociclib" AND "GEJ adenocarcinoma" AND "clinical trial"',
        '"CDK4/6" AND "gastric cancer" AND "radiation therapy" AND "sensitivity"'
    ]
    
    # Combine all queries
    all_queries = clinical_queries + cellular_queries + animal_queries + combined_queries
    
    return all_queries

def generate_detailed_markdown(analyzed_papers, keywords, search_queries, timestamp):
    """Generate detailed Markdown report of search results"""
    markdown = f"# Google Scholar Search Results for CDK4/6 Inhibitors and Gastroesophageal Junction Adenocarcinoma\n\n"

    # Add search information
    markdown += f"## Search Information\n\n"
    markdown += f"**Date:** {timestamp}\n\n"
    markdown += f"**Number of Papers:** {len(analyzed_papers)}\n\n"
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
    markdown = f"# References for CDK4/6 Inhibitors and Gastroesophageal Junction Adenocarcinoma\n\n"
    markdown += f"**Generated on:** {timestamp}\n\n"

    for i, (paper, _, _) in enumerate(analyzed_papers, 1):
        reference = format_reference(paper)
        markdown += f"{i}. {reference}\n\n"

    return markdown

def generate_categorized_references(analyzed_papers, timestamp):
    """Generate categorized references"""
    # Define categories
    categories = {
        "临床研究": ["gastroesophageal junction adenocarcinoma", "gej adenocarcinoma", "esophagogastric junction cancer", 
                  "clinical prognosis", "immunohistochemistry", "ihc", "ki-67", "prognostic model", "public database"],
        
        "细胞实验": ["in vitro", "cell cycle arrest", "apoptosis", "dna damage", "γ-h2ax", "mtt assay", 
                  "clonogenic assay", "radiotherapy", "radiosensitivity", "signaling pathway", 
                  "co-ip", "western blot", "reporter assay", "single-cell rna"],
        
        "动物模型": ["xenograft model", "mouse tumor model", "in vivo", "tumor regression", "tumor growth", 
                  "nude mice", "thermal imaging", "treatment response"],
        
        "CDK4/6抑制剂": ["palbociclib", "abemaciclib", "ribociclib", "cdk4/6 inhibitor", "cdk4/6 inhibition"],
        
        "放疗相关": ["radiotherapy", "radiation therapy", "radiosensitivity", "combined therapy"]
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
    markdown = f"# Categorized References for CDK4/6 Inhibitors and Gastroesophageal Junction Adenocarcinoma\n\n"
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
    parser = argparse.ArgumentParser(description="Search for academic papers related to CDK4/6 inhibitors and gastroesophageal junction adenocarcinoma")
    parser.add_argument("--num_papers", type=int, default=70, help="Number of papers to retrieve (default: 70)")
    args = parser.parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a timestamped directory
    timestamp_dir = f"search_results_{timestamp}"
    os.makedirs(timestamp_dir, exist_ok=True)
    
    # Get keywords
    print("Extracting CDK4/6 cancer research keywords...")
    keywords = get_cdk46_cancer_keywords()

    # Generate search queries
    search_queries = generate_search_queries()

    # Calculate papers per query
    papers_per_query = max(4, args.num_papers // len(search_queries))

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

    # Generate filenames without timestamps
    results_filename = "cdk46_cancer_search_results.md"
    references_filename = "cdk46_cancer_references.md"
    categorized_filename = "cdk46_cancer_categorized_references.md"
    data_filename = "cdk46_cancer_search_data.json"

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
    save_to_markdown(detailed_markdown, "cdk46_cancer_search_results_latest.md")
    save_to_markdown(reference_markdown, "cdk46_cancer_references_latest.md")
    save_to_markdown(categorized_markdown, "cdk46_cancer_categorized_references_latest.md")
    with open("cdk46_cancer_search_data_latest.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": formatted_timestamp,
            "search_queries": search_queries,
            "keywords": keywords,
            "papers": [p[0] for p in analyzed_papers]
        }, f, indent=2)

if __name__ == "__main__":
    main() 