from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Locators:
    SORT_NAME_BUTTON = (By.CSS_SELECTOR, '''[data-testid='sort-name-action']''')
    SORT_YEAR_BUTTON = (By.CSS_SELECTOR, '''[data-testid='sort-year-action']''')
    CLEAR_SORT_BUTTON = (By.CSS_SELECTOR, '''[data-testid='clear-sort-action']''')
    FAVORITES_LINK = (By.CSS_SELECTOR, '''[data-testid='nav-favorites']''')
    MOVIE_CARDS = (By.CSS_SELECTOR, '''[data-testid='film-entry']''')
    FAVORITE_BUTTON = (By.CSS_SELECTOR, '''[data-testid='favorite-icon']''')
    MOVIE_TITLES = (By.CSS_SELECTOR, '''[data-testid='film-entry'] .film-name''')
    MOVIE_YEARS = (By.CSS_SELECTOR, '''[data-testid='film-entry'] .film-release-year''')
    

class MovieAppPage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def sort_by_name(self):
        self.driver.find_element(*Locators.SORT_NAME_BUTTON).click()

    def sort_by_year(self):
        self.driver.find_element(*Locators.SORT_YEAR_BUTTON).click()
        
    def clear_sort(self):
        self.driver.find_element(*Locators.CLEAR_SORT_BUTTON).click()

    def get_movie_titles(self):
        self.wait.until(EC.presence_of_all_elements_located(Locators.MOVIE_TITLES))
        elements = self.driver.find_elements(*Locators.MOVIE_TITLES)
        return [elem.text for elem in elements]

    def get_movie_years(self):
        self.wait.until(EC.presence_of_all_elements_located(Locators.MOVIE_YEARS))
        elements = self.driver.find_elements(*Locators.MOVIE_YEARS)
        return [int(elem.text.strip('()')) for elem in elements]
        
    def go_to_favorites(self):
        self.driver.find_element(*Locators.FAVORITES_LINK).click()

    def add_first_movie_to_favorites(self):
        first_movie_card = self.wait.until(EC.presence_of_element_located(Locators.MOVIE_CARDS))
        
        # Get the full text of the card and extract the title part (first line)
        title = first_movie_card.text.split('\n')[0]
        
        # Find the favorite button *within the scope of this specific card*
        first_movie_card.find_element(*Locators.FAVORITE_BUTTON).click()
        
        return title