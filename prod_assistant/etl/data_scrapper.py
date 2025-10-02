# BS4 -> beautiful soupt -> HTML PArsing 
# Selenium -> browser lever -> interact with browser
# playwright -> automate browser tasks -> browser level 
import csv 
import time 
import re 
import os 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By 
from selenium.webdriver.edge.service import Service 
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

class FlipkartScraper:
    def __init__(self, output_dir = 'data'):
        """Initialize environment variables, embedding model, and set CSV file path"""
        print('Initializing DataScrapper pipeline....')

        self.output_dir = output_dir    
        os.makedirs(self.output_dir, exist_ok=True)
        self.edge_driver_path = Path('C:\\Users\\Suel.Abbasi\\OneDrive - Shell\\Desktop\\Projects\\ecommerce_chatbot\\msedgedriver.exe')

    def get_top_reviews(self, product_url, count=2):
        """Get Top Reviews for the product at the given URL."""
        options = Options()
        options.add_argument('--headless')
        options.use_chromium = True 
        service = Service(self.edge_driver_path)
        driver = webdriver.Edge(service=service, options=options)

        if not product_url.startswith('http'):
            return "No reviews found"
        
        try:
            driver.get(product_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))
            try:
                # Close the login popup if it appears
                close_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "X")]'))
                )
                close_btn.click()
                time.sleep(2)
            except Exception as e:
                print(f'No popup to close: {e}')

            # Scroll to load reviews
            for _ in range(4):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co") 
            seen = set() 
            reviews = []

            for block in review_blocks:
                text = block.get_text(separator=' ', strip=True)  # <-- FIXED HERE
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text) 
                
                if len(reviews) >= count:
                    break 
        except Exception as e:
            print(f"Error while scraping reviews: {e}")  # <-- Print error for debugging
            reviews = []

        driver.quit() 
        return " || ".join(reviews) if reviews else "No reviews found"

    def scrape_flipkart_product(self, query, max_products=1, review_count=2):
        """Scrape Flipkart products based on a search query"""
        options = Options()
        options.add_argument('--headless')
        options.use_chromium = True 
        service = Service(self.edge_driver_path)  # <-- Use the same path as in __init__
        driver = webdriver.Edge(service=service, options=options)
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Try to close login popup if it appears
        try:
            close_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "X")]'))
            )
            close_btn.click()
        except Exception:
            pass

        time.sleep(2) 
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, 'div[data-id]')[:max_products]
        for item in items: 
            try:
                title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
                rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
                reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"
            except Exception as e:
                print(f'Error occurred while processing item: {e}')
                continue

            top_reviews = self.get_top_reviews(product_link, count=review_count) if 'flipkart.com' in product_link else "Invalid product URL"
            products.append([product_id,title,rating,total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename='product_reviews.csv'):
        """Save the scraped product reviews to a CSV file."""
        if os.path.isabs(filename):
            path = filename
        elif os.path.dirname(filename):  # filename includes subfolder like 'data/product_reviews.csv'
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            # plain filename like 'output.csv'
            path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)