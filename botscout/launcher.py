# launcher.py
import requests
from selenium import webdriver
from ._launcher_utils import _prepare_url
from selenium.webdriver.chrome.options import Options


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
    ip = check_ip()
    url = _prepare_url(url)
    print("Launcher ", url, ". Current ip address is ", ip)

    chrome_options = Options()
    if keep_open:
        chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return "200"


