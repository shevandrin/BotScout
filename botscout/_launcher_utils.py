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
    generated_xpaths = [f"//button[contains(., '{phrase}')]" for phrase in text_phrases]
    common_button_xpaths = generated_xpaths + literal_xpaths
    print("Checking for cookie consent banner...")

    for xpath in common_button_xpaths:
        # Find the button using the current XPath
        consent_buttons = driver.find_elements(By.XPATH, xpath)
        for button in consent_buttons:
            try:
                # If found, try to click it
                if button.is_displayed() and button.is_enabled():
                    print(f"  - Found consent button with XPath: {xpath}")
                    button.click()
                    print("  - Clicked the consent button.")
                    time.sleep(1)
                    return
            except NoSuchElementException:
                # This is expected: the button for this XPath doesn't exist.
                continue
            except ElementClickInterceptedException:
                # The button might be temporarily unclickable, try a JS click.
                print("  - Regular click intercepted, trying JavaScript click.")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                return
            except Exception as e:
                # Catch any other unexpected errors
                print(f"  - An unexpected error occurred: {e}")
                continue
    print("  - No cookie consent banner found, or it was already handled.")


def _click_element_from_data(driver: WebDriver, element_data: dict):
    """
    Intelligently clicks an element based on the data returned by the JS script.
    It correctly handles elements inside iframes.

    Args:
        driver: The active Selenium WebDriver instance.
        element_data: A dictionary for a single element from the JS result.
    """
    element_xpath = element_data.get('xpath')
    iframe_xpath = element_data.get('iframe_xpath')

    if not element_xpath:
        print("Error: Element data is missing 'xpath'. Cannot click.")
        return

    # This is the path that will be executed for your data
    if iframe_xpath:
        print(f"Element is inside an iframe. Locating iframe with XPath: {iframe_xpath}")
        try:
            # 1. Find the iframe element in the main document.
            iframe_element = driver.find_element(By.XPATH, iframe_xpath)

            # 2. Switch the driver's context to this iframe.
            print("Switching context to iframe...")
            driver.switch_to.frame(iframe_element)

            # 3. Now, inside the iframe, find the target element by ITS xpath.
            print(f"Finding element inside iframe with XPath: {element_xpath}")
            target_element = driver.find_element(By.XPATH, element_xpath)

            # 4. Click the element.
            print("Clicking element.")
            target_element.click()

        except NoSuchElementException as e:
            print(f"Error: Could not find element or iframe. Details: {e}")
        finally:
            # 5. CRITICAL: Always switch back to the main document context.
            print("Switching context back to the main document.")
            driver.switch_to.default_content()

    else:  # This path is for elements not in an iframe
        print(f"Element is in the main document. Finding with XPath: {element_xpath}")
        try:
            target_element = driver.find_element(By.XPATH, element_xpath)
            print("Clicking element.")
            target_element.click()
        except NoSuchElementException as e:
            print(f"Error: Could not find element in main document. Details: {e}")
