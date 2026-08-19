from Bio import Entrez
import time
import csv
from datetime import datetime
import os

# Configuration
Entrez.email = "your_email@example.com"  # REQUIRED: Set your email
API_KEY = None  # Optional: Get from NCBI for higher rate limits

# Set API key if you have one
if API_KEY:
    Entrez.api_key = API_KEY


def search_and_fetch_paper(title):
    """Search PubMed for a paper by title and fetch its information.
    
    Args:
        title (str): The paper title to search for
        
    Returns:
        dict: Contains pmid, title, and medline_data, or None if not found
    """
    try:
        # Search for the paper
        handle = Entrez.esearch(db="pubmed", term=f'"{title}"[Title]', retmax=1)
        record = Entrez.read(handle)
        handle.close()
        
        if not record["IdList"]:
            return None
        
        pmid = record["IdList"][0]
        
        # Fetch detailed information
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
        data = handle.read()
        handle.close()
        
        return {
            "pmid": pmid,
            "title": title,
            "medline_data": data
        }
    except Exception as e:
        print(f"Error searching for '{title}': {str(e)}")
        return None


def batch_download_papers(titles_list, output_dir="pubmed_downloads"):
    """Batch download papers from a list of titles.
    
    Args:
        titles_list (list): List of paper titles to download
        output_dir (str): Directory to save downloaded papers (default: pubmed_downloads)
        
    Returns:
        list: List of results with title, PMID, status, and filename
    """
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    successful = 0
    failed = 0
    
    print(f"\n{'='*60}")
    print(f"Starting PubMed Batch Download")
    print(f"Total papers to download: {len(titles_list)}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}\n")
    
    for idx, title in enumerate(titles_list, 1):
        print(f"[{idx}/{len(titles_list)}] Searching for: {title[:60]}...")
        
        paper = search_and_fetch_paper(title)
        
        if paper:
            # Clean filename
            safe_title = "".join(c for c in paper['title'] if c.isalnum() or c in (' ', '_', '-'))[:50]
            filename = os.path.join(output_dir, f"{paper['pmid']}_{safe_title}.txt")
            
            # Save to individual file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(paper['medline_data'])
            
            results.append({
                "Title": title,
                "PMID": paper['pmid'],
                "Status": "Downloaded",
                "Filename": filename
            })
            successful += 1
            print(f"  ✓ Downloaded (PMID: {paper['pmid']})")
        else:
            results.append({
                "Title": title,
                "PMID": "Not Found",
                "Status": "Failed",
                "Filename": ""
            })
            failed += 1
            print(f"  ✗ Not found on PubMed")
        
        # Rate limiting: be respectful to NCBI servers
        time.sleep(0.5)
    
    # Save results to CSV
    csv_filename = os.path.join(output_dir, f"download_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "PMID", "Status", "Filename"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print(f"Download Complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Results saved to: {csv_filename}")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    # Example usage
    paper_titles = [
        "CRISPR-Cas9 genome editing in human cells",
        "Deep learning in medical imaging",
        "Machine learning for drug discovery",
    ]
    
    batch_download_papers(paper_titles)
