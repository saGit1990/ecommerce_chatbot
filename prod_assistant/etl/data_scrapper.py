import csv
import time
import re
import os
import logging
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO)

class FlipkartScraper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_top_reviews(self,product_url,count=2):
        """Get the top reviews for a product.
        """
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        # set a common user-agent to reduce bot-detection differences
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.page_load_strategy = "eager"
        driver = uc.Chrome(options=options, use_subprocess=True)

        if not product_url.startswith("http"):
            return "No reviews found"

        try:
            driver.get(product_url)
            time.sleep(4)
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
                time.sleep(1)
            except Exception as e:
                print(f"Error occurred while closing popup: {e}")

            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
            # Debug info to help diagnose empty results
            logging.info(f"Page title: {driver.title}")
            logging.info(f"Page source length: {len(driver.page_source)}")
            logging.info(f"Initial review blocks found: {len(review_blocks)}")

            # Fallback: try to find divs that contain the word 'review' if initial selectors fail
            if not review_blocks:
                for div in soup.find_all("div"):
                    text = div.get_text(separator=" ", strip=True)
                    if text and 'review' in text.lower() and len(text) > 40:
                        review_blocks.append(div)
                logging.info(f"Fallback review blocks found: {len(review_blocks)}")
            seen = set()
            reviews = []

            for block in review_blocks:
                text = block.get_text(separator=" ", strip=True)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= count:
                    break
        except Exception as e:
            logging.exception("Error while fetching top reviews")
            reviews = []

        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"
    
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        """Scrape Flipkart products based on a search query.
        """
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        driver = uc.Chrome(options=options, use_subprocess=True)
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except Exception as e:
            logging.debug(f"Popup close not found or failed: {e}")

        time.sleep(2)
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        logging.info(f"Found {len(items)} product container items")
        for item in items:
            try:
                # title/price/rating selectors on Flipkart change frequently; try a couple of fallbacks
                try:
                    title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
                except Exception:
                    title = item.text.strip().split('\n')[0]

                try:
                    price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
                except Exception:
                    price = "N/A"

                try:
                    rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
                except Exception:
                    rating = "N/A"

                try:
                    reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
                except Exception:
                    reviews_text = ""

                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href and href.startswith("http") else ("https://www.flipkart.com" + href if href else "")
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href or "")
                product_id = match[0] if match else "N/A"
                logging.info(f"Product found: title='{title[:60]}', href='{product_link}', id='{product_id}'")
            except Exception as e:
                print(f"Error occurred while processing item: {e}")
                continue

            top_reviews = self.get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
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
        