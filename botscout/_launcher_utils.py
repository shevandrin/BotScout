from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
from .patterns import COOKIE_PATTERNS


def _prepare_url(url: str) -> str:
    """
    Ensures the URL starts with 'http://' or 'https://'
    and ends with a trailing slash '/'.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if not url.endswith("/"):
        url += "/"

    return url


def _handle_cookie_consent(driver: WebDriver):
    """
    Attempts to find and click a cookie consent button.

    This function uses a list of common XPath selectors for cookie banners
    and tries to click them. It fails gracefully if no banner is found.

    Args:
        driver: The active Selenium WebDriver instance.
    """

    time.sleep(2)
    # Forming a list of common patterns for "accept" buttons.
    text_phrases = COOKIE_PATTERNS.get('button_text_phrases', [])
    literal_xpaths = COOKIE_PATTERNS.get('literal_xpaths', [])
    generated_xpaths = [f"//button[contains(text(), '{phrase}')]" for phrase in text_phrases]
    common_button_xpaths = generated_xpaths + literal_xpaths
    print("Checking for cookie consent banner...")
    for xpath in common_button_xpaths:
        try:
            # Find the button using the current XPath
            consent_button = driver.find_element(By.XPATH, xpath)

            # If found, try to click it
            if consent_button.is_displayed() and consent_button.is_enabled():
                print(f"  - Found consent button with XPath: {xpath}")
                consent_button.click()
                print("  - Clicked the consent button.")
                time.sleep(1)
                return
        except NoSuchElementException:
            # This is expected: the button for this XPath doesn't exist.
            continue
        except ElementClickInterceptedException:
            # The button might be temporarily unclickable, try a JS click.
            print("  - Regular click intercepted, trying JavaScript click.")
            driver.execute_script("arguments[0].click();", consent_button)
            time.sleep(1)
            return
        except Exception as e:
            # Catch any other unexpected errors
            print(f"  - An unexpected error occurred: {e}")
            continue

    print("  - No cookie consent banner found, or it was already handled.")
