#!/usr/bin/env python3
"""
DOM Fetcher for React Applications
Captures full HTML DOMs using headless Selenium
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class DOMFetcher:
    def __init__(self, headless: bool = True, wait_timeout: int = 15):
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Chrome WebDriver with optimal settings"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("log-level=3")

            # --- FIX: Use Selenium's built-in Selenium Manager ---
            # This is more robust than webdriver-manager and avoids version mismatch errors.
            # We simply remove the explicit `service` object.
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized successfully using Selenium Manager.")
            
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            raise
    
    def fetch_dom(self, url: str, wait_for_element: str = "body") -> Dict:
        """Fetch DOM from a given URL"""
        try:
            print(f"🌐 Fetching DOM from: {url}")
            self.driver.get(url)
            
            # Wait for a basic element to ensure the page has started rendering
            wait = WebDriverWait(self.driver, self.wait_timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            
            # Give React apps a moment to fully hydrate the DOM
            time.sleep(2)
            
            dom_html = self.driver.page_source
            
            return {
                "url": url,
                "title": self.driver.title,
                "html": dom_html,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except (TimeoutException, WebDriverException) as e:
            error_msg = f"Error fetching DOM from {url}: {e}"
            print(f"❌ {error_msg}")
            return {"url": url, "error": error_msg, "success": False}
    
    def save_dom_to_file(self, dom_data: Dict, filepath: str):
        """Save DOM data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dom_data, f, indent=2, ensure_ascii=False)
            print(f"💾 DOM for {dom_data.get('url')} saved to: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save DOM: {str(e)}")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ WebDriver closed successfully")
            except Exception as e:
                print(f"⚠️  Warning: Error closing WebDriver: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()