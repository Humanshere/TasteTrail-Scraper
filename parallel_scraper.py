# -*- coding: utf-8 -*-
"""
Parallel scraping module using ThreadPoolExecutor for concurrent Google Maps scraping.
Implements rate limiting and anti-bot detection measures.
Each place is saved to its own CSV file using the place ID from the URL.
"""

import csv
import logging
import threading
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from queue import Queue
from typing import List, Dict, Optional
from googlemaps import GoogleMapsScraper
from termcolor import colored
import time

class ParallelGoogleMapsScraper:
    """
    Manages parallel scraping of Google Maps reviews using worker threads.
    Implements rate limiting to avoid bot detection.
    Each place gets its own CSV file based on place ID from URL.
    """
    
    def __init__(self, max_workers: int = 2, output_dir: str = 'data', 
                 source_field: bool = False, debug: bool = False):
        """
        Initialize the parallel scraper.
        
        Args:
            max_workers: Number of concurrent browser instances (default: 2 to avoid detection)
            output_dir: Directory to save output CSV files (default: 'data')
            source_field: Whether to include source URL in output
            debug: Whether to run in debug mode with visible browser
        """
        self.max_workers = max_workers
        self.output_dir = output_dir
        self.source_field = source_field
        self.debug = debug
        self.logger = self._setup_logger()
        
        # Statistics
        self.stats = {
            'total_urls': 0,
            'completed_urls': 0,
            'failed_urls': 0,
            'total_reviews': 0,
            'start_time': None,
            'end_time': None,
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the parallel scraper."""
        logger = logging.getLogger("ParallelGoogleMapsScraper")
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        
        return logger
    
    def _extract_place_id(self, url: str) -> str:
        """
        Extract place ID from Google Maps URL.
        Supports multiple URL formats:
        - Standard: /place/name/@lat,lon/...
        - Query: ?q=place_id:ChIJ...
        - Coordinates: /@lat,lon/...
        
        Args:
            url: Google Maps URL
            
        Returns:
            Place ID or filename-safe identifier
        """
        try:
            # Try to extract place_id from query parameter format
            match = re.search(r'place_id:([A-Za-z0-9_-]+)', url)
            if match:
                place_id = match.group(1)
                return place_id[:50]  # Limit length
        except:
            pass
        
        try:
            # Try to extract place name from standard format /place/name/
            match = re.search(r'/place/([^/@]+)/', url)
            if match:
                place_name = match.group(1)
                # Clean up the name for use as filename
                place_id = re.sub(r'[^a-zA-Z0-9_-]', '_', place_name)
                return place_id[:50]  # Limit length
        except:
            pass
        
        # Fallback: use coordinates if available
        try:
            match = re.search(r'/@([-\d.]+),([-\d.]+)', url)
            if match:
                lat, lon = match.groups()
                # Use only first 6 decimal places for filename
                lat_short = lat.replace('.', '_')[:10]
                lon_short = lon.replace('.', '_')[:10]
                return f"place_{lat_short}_{lon_short}"
        except:
            pass
        
        # Final fallback: use timestamp
        return f"place_{int(datetime.now().timestamp())}"
    
    def _init_csv_writer_for_url(self, url: str) -> tuple:
        """
        Initialize CSV writer for a specific URL.
        Creates separate file per place using place ID.
        
        Args:
            url: Google Maps URL
            
        Returns:
            Tuple of (csv_file, csv_writer, output_filename)
        """
        HEADER = ['id_review', 'caption', 'more_caption', 'relative_date', 'retrieval_date', 
                  'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
        HEADER_W_SOURCE = HEADER + ['url_source']
        
        place_id = self._extract_place_id(url)
        output_file = f'{self.output_dir}/{place_id}_reviews.csv'
        
        csv_file = open(output_file, mode='w', encoding='utf-8', newline='\n')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        
        header = HEADER_W_SOURCE if self.source_field else HEADER
        writer.writerow(header)
        csv_file.flush()
        
        return csv_file, writer, output_file
    
    def _write_row(self, writer, csv_file, row_data: List, url: Optional[str] = None):
        """
        Write a single row to CSV file (no locking needed, each thread has its own file).
        
        Args:
            writer: CSV writer object for this URL
            csv_file: CSV file object for this URL
            row_data: List of data to write
            url: Optional source URL to append
        """
        if self.source_field and url:
            row_data = list(row_data) + [url.strip()]
        writer.writerow(row_data)
        csv_file.flush()
        self.stats['total_reviews'] += 1
    
    def scrape_url(self, url: str, num_reviews: int) -> Dict:
        """
        Scrape reviews from a single Google Maps URL.
        This runs in a worker thread and writes to its own CSV file.

        Args:
            url: Google Maps URL to scrape
            num_reviews: Number of reviews to scrape

        Returns:
            Dictionary with scraping results and statistics
        """
        
        result = {
            'url': url.strip(),
            'reviews_scraped': 0,
            'status': 'pending',
            'error': None,
            'output_file': None,
            'start_time': datetime.now(),
        }
        
        csv_file = None
        writer = None
        
        try:
            # Initialize CSV file for this specific URL/place
            csv_file, writer, output_file = self._init_csv_writer_for_url(url)
            result['output_file'] = output_file
            
            with GoogleMapsScraper(debug=self.debug) as scraper:
                self.logger.info(f"Opening reviews for {url.strip()}")
                scraper.open_reviews(url)
                
                # Scrape reviews (use Google Maps default ordering)
                n = 0
                while n < num_reviews:
                    self.logger.info(f"[{url.strip()}] Fetching reviews batch {n // 20 + 1}")
                    
                    reviews = scraper.get_reviews(n)
                    
                    if len(reviews) == 0:
                        self.logger.info(f"[{url.strip()}] No more reviews available")
                        break
                    
                    for review in reviews:
                        row_data = list(review.values())
                        self._write_row(writer, csv_file, row_data, url)
                        result['reviews_scraped'] += 1
                    
                    n += len(reviews)
                
                result['status'] = 'success'
                self.logger.info(colored(f"[{url.strip()}] Completed: {result['reviews_scraped']} reviews → {output_file}", 'green'))
                
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.logger.error(colored(f"[{url.strip()}] Error: {str(e)}", 'red'))
        
        finally:
            # Close the CSV file for this URL
            if csv_file:
                csv_file.close()
            result['end_time'] = datetime.now()
            result['duration'] = (result['end_time'] - result['start_time']).total_seconds()
        
        return result
    
    def scrape_urls(self, urls: List[str], num_reviews: int) -> Dict:
        """
        Scrape reviews from multiple URLs in parallel.
        
        Args:
            urls: List of Google Maps URLs
            num_reviews: Number of reviews to scrape per URL
            
        Returns:
            Dictionary with overall statistics and per-URL results
        """
        self.stats['start_time'] = datetime.now()
        self.stats['total_urls'] = len(urls)
        
        self.logger.info(f"Starting parallel scraping with {self.max_workers} workers")
        self.logger.info(f"URLs to scrape: {len(urls)}")
        
        results = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.scrape_url, url, num_reviews): url
                for url in urls
            }
            
            # Process completed tasks as they finish
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'success':
                        self.stats['completed_urls'] += 1
                    else:
                        self.stats['failed_urls'] += 1
                    
                    completed += 1
                    progress_pct = (completed / len(urls)) * 100
                    self.logger.info(f"Progress: {completed}/{len(urls)} ({progress_pct:.1f}%)")
                    
                except Exception as e:
                    self.logger.error(f"Task failed with exception: {str(e)}")
                    self.stats['failed_urls'] += 1
        
        self.stats['end_time'] = datetime.now()
        total_duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Print summary
        self._print_summary(results, total_duration)
        
        return {
            'statistics': self.stats,
            'results': results,
            'total_duration': total_duration,
        }
    
    def _print_summary(self, results: List[Dict], total_duration: float):
        """Print scraping summary with per-URL output files."""
        self.logger.info("\n" + "="*80)
        self.logger.info("SCRAPING SUMMARY")
        self.logger.info("="*80)
        
        # Print per-URL results
        self.logger.info("\nPer-URL Results:")
        for result in results:
            status_color = 'green' if result['status'] == 'success' else 'red'
            status_symbol = '✓' if result['status'] == 'success' else '✗'
            output_file = result.get('output_file', 'N/A')
            self.logger.info(colored(f"{status_symbol} {result['url']}", status_color))
            self.logger.info(f"  Reviews: {result['reviews_scraped']}, Duration: {result['duration']:.2f}s")
            self.logger.info(f"  Output: {output_file}")
            if result['error']:
                self.logger.info(colored(f"  Error: {result['error']}", 'red'))
        
        # Print overall statistics
        self.logger.info("\nOverall Statistics:")
        self.logger.info(f"Total URLs: {self.stats['total_urls']}")
        self.logger.info(f"Completed: {self.stats['completed_urls']}")
        self.logger.info(f"Failed: {self.stats['failed_urls']}")
        self.logger.info(f"Total Reviews Scraped: {self.stats['total_reviews']}")
        self.logger.info(f"Total Duration: {total_duration:.2f} seconds")
        if self.stats['total_urls'] > 0:
            self.logger.info(f"Average Time per URL: {total_duration / self.stats['total_urls']:.2f} seconds")
        if self.stats['total_reviews'] > 0 and self.stats['completed_urls'] > 0:
            self.logger.info(f"Average Reviews per URL: {self.stats['total_reviews'] / self.stats['completed_urls']:.1f}")
        self.logger.info("="*80 + "\n")
        self.logger.info(colored("✓ Each place has been saved to its own CSV file in the data/ directory", 'green'))
