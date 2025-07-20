import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import sys # Import the sys module
import importlib

class MovieAppTests(unittest.TestCase):
    driver = None
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("log-level=3")
        if cls.driver is None:
            cls.driver = webdriver.Chrome(options=chrome_options)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
            cls.driver = None

    def setUp(self):
        selector_module_name = os.environ.get("SELECTOR_MODULE", "page_selectors.page_v1")
        page_module = importlib.import_module(selector_module_name)
        self.app_url = os.environ.get("TEST_URL")
        if not self.app_url: self.fail("TEST_URL environment variable not set!")
        self.driver.get(self.app_url)
        self.movie_page = page_module.MovieAppPage(self.driver)
        time.sleep(1)

    def test_sort_by_name(self):
        self.movie_page.sort_by_name()
        time.sleep(1)
        titles = self.movie_page.get_movie_titles()
        self.assertGreater(len(titles), 0, "No movies found to test sorting.")
        self.assertListEqual(titles, sorted(titles), "Movies are not sorted correctly by name.")

    def test_sort_by_release_year(self):
        self.movie_page.sort_by_year()
        time.sleep(1)
        years = self.movie_page.get_movie_years()
        self.assertGreater(len(years), 0, "No movies found to test sorting.")
        self.assertListEqual(years, sorted(years, reverse=True), "Movies are not sorted correctly by year.")

    def test_add_and_verify_favorite(self):
        favorited_movie_title = self.movie_page.add_first_movie_to_favorites()
        self.movie_page.go_to_favorites()
        time.sleep(1)
        favorite_titles = self.movie_page.get_movie_titles()
        self.assertIn(favorited_movie_title, favorite_titles, "Favorited movie not found on the favorites page.")

    def test_clear_sort(self):
        initial_titles = self.movie_page.get_movie_titles()
        self.movie_page.sort_by_name()
        time.sleep(1)
        self.movie_page.clear_sort()
        time.sleep(1)
        cleared_titles = self.movie_page.get_movie_titles()
        self.assertListEqual(initial_titles, cleared_titles, "Clearing sort did not return movies to the original order.")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MovieAppTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # --- THIS IS THE FIX ---
    # Exit with a non-zero code if the test suite was not successful.
    # This correctly signals failure to the run_demo.py orchestrator.
    sys.exit(not result.wasSuccessful())