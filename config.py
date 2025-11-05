# -*- coding: utf-8 -*-
"""
Advanced configuration and utilities for parallel scraping.
Includes rate limiting, proxy management, and performance tuning.
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

class ScrapingSpeed(Enum):
    """Scraping speed presets with delay configurations."""
    CAUTIOUS = {
        'scroll_delay': (1.5, 3.0),
        'click_delay': (1.5, 3.0),
        'load_delay': (5.0, 8.0),
        'workers': 1,
        'description': 'Maximum stealth, minimum speed'
    }
    NORMAL = {
        'scroll_delay': (0.8, 2.0),
        'click_delay': (0.8, 2.0),
        'load_delay': (3.0, 6.0),
        'workers': 2,
        'description': 'Balanced speed and stealth'
    }
    FAST = {
        'scroll_delay': (0.3, 1.0),
        'click_delay': (0.5, 1.5),
        'load_delay': (2.0, 4.0),
        'workers': 3,
        'description': 'Higher speed, higher detection risk'
    }
    AGGRESSIVE = {
        'scroll_delay': (0.1, 0.5),
        'click_delay': (0.2, 0.8),
        'load_delay': (1.0, 2.0),
        'workers': 4,
        'description': 'Maximum speed, very high detection risk'
    }

@dataclass
class ScraperConfig:
    """Configuration for parallel scraper."""
    max_workers: int = 2
    speed_mode: ScrapingSpeed = ScrapingSpeed.NORMAL
    enable_proxy: bool = False
    proxy_list: Optional[List[str]] = None
    enable_vpn_rotation: bool = False
    request_timeout: int = 30
    retry_attempts: int = 3
    headless: bool = True
    disable_images: bool = True
    disable_css: bool = False
    user_agent_rotation: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.max_workers > 4:
            print("⚠️  Warning: More than 4 workers significantly increases detection risk!")
        
        if self.speed_mode == ScrapingSpeed.AGGRESSIVE:
            print("⚠️  Warning: AGGRESSIVE mode has very high bot detection risk!")
    
    def get_delay_config(self):
        """Get delay configuration for current speed mode."""
        return self.speed_mode.value

# Predefined configurations for common scenarios
CONFIGS = {
    'safe': ScraperConfig(
        max_workers=1,
        speed_mode=ScrapingSpeed.CAUTIOUS,
        user_agent_rotation=True,
    ),
    'balanced': ScraperConfig(
        max_workers=2,
        speed_mode=ScrapingSpeed.NORMAL,
        user_agent_rotation=True,
    ),
    'fast': ScraperConfig(
        max_workers=3,
        speed_mode=ScrapingSpeed.FAST,
        user_agent_rotation=True,
    ),
    'aggressive': ScraperConfig(
        max_workers=4,
        speed_mode=ScrapingSpeed.AGGRESSIVE,
        user_agent_rotation=True,
    ),
}

def get_config(preset: str = 'balanced') -> ScraperConfig:
    """Get predefined configuration by preset name."""
    return CONFIGS.get(preset, CONFIGS['balanced'])

# Sample proxy list (replace with real proxies)
PROXY_LIST = [
    # Format: 'http://proxy1.com:8080'
    # Format with auth: 'http://user:pass@proxy.com:8080'
]

# Browser options for different scenarios
CHROME_OPTIONS_STEALTH = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-extensions',
    '--disable-default-apps',
    '--disable-plugins-power-saving-mode',
    '--disable-client-side-phishing-detection',
    '--disable-web-resources',
]

CHROME_OPTIONS_SPEED = [
    '--disable-images',
    '--disable-css',
    '--disable-notifications',
    '--disable-infobars',
]

# List of realistic user agents
USER_AGENTS_DESKTOP = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

USER_AGENTS_MOBILE = [
    'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
]

def get_user_agent(mobile: bool = False) -> str:
    """Get a random realistic user agent."""
    from random import choice
    agents = USER_AGENTS_MOBILE if mobile else USER_AGENTS_DESKTOP
    return choice(agents)

# Performance tuning utilities
def estimate_scraping_time(num_urls: int, reviews_per_url: int, workers: int = 2, 
                          seconds_per_review: float = 2.0) -> float:
    """
    Rough estimate of scraping time.
    
    Args:
        num_urls: Number of URLs to scrape
        reviews_per_url: Average reviews per URL
        workers: Number of parallel workers
        seconds_per_review: Average seconds to scrape one review
        
    Returns:
        Estimated time in seconds
    """
    total_reviews = num_urls * reviews_per_url
    base_time = total_reviews * seconds_per_review
    parallel_speedup = min(workers, num_urls) * 0.85  # 85% efficiency
    return base_time / parallel_speedup

def format_time(seconds: float) -> str:
    """Format seconds into human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

# Example usage
if __name__ == '__main__':
    # Get different configs
    safe_config = get_config('safe')
    balanced_config = get_config('balanced')
    fast_config = get_config('fast')
    
    print("Safe Config:", safe_config)
    print("\nBalanced Config:", balanced_config)
    print("\nFast Config:", fast_config)
    
    # Estimate scraping time
    estimated_time = estimate_scraping_time(
        num_urls=10,
        reviews_per_url=50,
        workers=2
    )
    print(f"\nEstimated time for 10 URLs × 50 reviews with 2 workers: {format_time(estimated_time)}")
