#!/usr/bin/env python
"""Command-line interface for PubMed Batch Downloader."""

import argparse
import pandas as pd
from pubmed_downloader import batch_download_papers


def main():
    parser = argparse.ArgumentParser(
        description="Batch download papers from PubMed by title",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --titles paper_titles.csv
  python main.py --titles paper_titles.csv --output my_downloads
        """
    )
    
    parser.add_argument(
        "--titles",
        required=True,
        help="CSV file containing paper titles (column name: 'Title')"
    )
    
    parser.add_argument(
        "--output",
        default="pubmed_downloads",
        help="Output directory for downloaded papers (default: pubmed_downloads)"
    )
    
    args = parser.parse_args()
    
    try:
        # Read CSV file
        print(f"Reading titles from: {args.titles}")
        df = pd.read_csv(args.titles)
        
        if 'Title' not in df.columns:
            print("Error: CSV file must contain a 'Title' column")
            return
        
        titles = df['Title'].tolist()
        print(f"Found {len(titles)} titles to process\n")
        
        # Download papers
        batch_download_papers(titles, output_dir=args.output)
        
    except FileNotFoundError:
        print(f"Error: File '{args.titles}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
