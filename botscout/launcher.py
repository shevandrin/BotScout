# launcher.py
import requests
from selenium import webdriver
from ._launcher_utils import _prepare_url, _handle_cookie_consent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def check_ip():
    """
    Returns the current public IP address of the machine.

    Returns:
        str: The public IP address, or None if the request fails.
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException:
        return None
    except Exception as e:
        print(f"An unexpected error occurred in check_ip: {e}")
        return None


def launch_page(url="https://www.google.com/", keep_open=True):
    """Launches a Chrome browser to the specified URL.

    Args:
        url (str): The URL to open.
        keep_open (bool): If True, the browser window will remain open
            after the function finishes. Defaults to True.

    Returns:
        driver: Selenium Chrome webdriver.
    """
    ip = check_ip()
    url = _prepare_url(url)
    print("Launcher ", url, ". Current ip address is ", ip)

    chrome_options = Options()
    if keep_open:
        chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    _handle_cookie_consent(driver)

    return driver
