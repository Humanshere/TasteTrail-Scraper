# -*- coding: utf-8 -*-
"""
Optimized Google Maps Reviews Scraper with Parallel Processing
Supports concurrent scraping with anti-bot detection measures.
"""

from parallel_scraper import ParallelGoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time

ind = {'most_relevant': 0, 'newest': 1, 'highest_rating': 2, 'lowest_rating': 3}
HEADER = ['id_review', 'caption', 'more_caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'more_caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper with parallel processing.')
    parser.add_argument('--N', type=int, default=10, help='Number of reviews to scrape per URL')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--o', type=str, default='output.csv', help='output file name (in data/ directory)')
    # sorting intentionally removed: always use Google Maps default order
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file')
    parser.add_argument('--workers', type=int, default=2, help='Number of parallel workers (default: 2, max: 4)')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()
    
    # Validate worker count (too many workers will trigger bot detection)
    workers = min(args.workers, 4) if not args.debug else 1
    
    print(colored(f"Starting Google Maps Reviews Scraper", 'cyan'))
    print(colored(f"Configuration:", 'cyan'))
    print(f"  - Input file: {args.i}")
    print(f"  - Output file: data/{args.o}")
    print(f"  - Reviews per URL: {args.N}")
    print(f"  - Sort: using Google Maps default order")
    print(f"  - Parallel workers: {workers}")
    print(f"  - Debug mode: {args.debug}")
    print(colored(f"Note: Using anti-bot detection measures for all requests\n", 'yellow'))
    
    if args.place:
        print(colored("Place metadata scraping not yet implemented with parallel processing", 'red'))
    else:
        # Read URLs from file
        try:
            with open(args.i, 'r') as urls_file:
                urls = [url.strip() for url in urls_file.readlines() if url.strip()]
        except FileNotFoundError:
            print(colored(f"Error: File '{args.i}' not found", 'red'))
            exit(1)
        
        if not urls:
            print(colored(f"Error: No URLs found in '{args.i}'", 'red'))
            exit(1)
        
        # Create parallel scraper
        scraper = ParallelGoogleMapsScraper(
            max_workers=workers,
            output_dir='data',
            source_field=args.source,
            debug=args.debug
        )
        
        try:
            # Start scraping
            print(colored(f"Starting parallel scraping of {len(urls)} URL(s)...\n", 'green'))
            results = scraper.scrape_urls(urls, args.N)
            
            # Print detailed results
            print(colored("\nDetailed Results per URL:", 'cyan'))
            print("-" * 100)
            for result in results['results']:
                status_color = 'green' if result['status'] == 'success' else 'red'
                print(colored(f"URL: {result['url']}", status_color))
                print(f"  Status: {result['status']}")
                print(f"  Reviews: {result['reviews_scraped']}")
                print(f"  Duration: {result['duration']:.2f}s")
                print(f"  Output File: {result.get('output_file', 'N/A')}")
                if result['error']:
                    print(colored(f"  Error: {result['error']}", 'red'))
                print()
            
            # Print final summary
            stats = results['statistics']
            print(colored("="*100, 'cyan'))
            print(colored("FINAL SUMMARY", 'cyan'))
            print(colored("="*100, 'cyan'))
            print(f"Total URLs processed: {stats['completed_urls'] + stats['failed_urls']}/{stats['total_urls']}")
            print(f"Successfully completed: {stats['completed_urls']}")
            print(f"Failed: {stats['failed_urls']}")
            print(f"Total reviews scraped: {stats['total_reviews']}")
            print(f"Total time: {results['total_duration']:.2f} seconds")
            if stats['total_urls'] > 0:
                print(f"Average time per URL: {results['total_duration'] / stats['total_urls']:.2f} seconds")
            print(colored("="*100 + "\n", 'cyan'))
            
            print(colored(f"✓ Output saved to: data/ (each place in its own CSV file)", 'green'))
            print(colored("✓ Scraping completed successfully!", 'green'))
            
        finally:
            pass  # No need to close shared file as each thread manages its own

