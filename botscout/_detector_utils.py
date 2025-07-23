from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


def _find_elements_by_computed_style(driver: WebDriver):
    """
    Finds all elements that match specific computed style properties
    common to chatbot widgets (e.g., fixed position, high z-index).

    Returns:
        A list of WebElements that match the style criteria.
    """

    javascript_to_execute = """
    function findElementsByStyle() {
        const matchingElements = [];
        const candidateElements = document.querySelectorAll('div, iframe, button, a');
        
        for (const element of candidateElements) {
            const style = window.getComputedStyle(element);
            
            const position = style.getPropertyValue('position');
            const zIndex = parseInt(style.getPropertyValue('z-index'), 10) || 0;
            const bottom = parseInt(style.getPropertyValue('bottom'), 10) || 0;
            const right = parseInt(style.getPropertyValue('right'), 10) || 0;
            const display = style.getPropertyValue('display');
            const visibility = style.getPropertyValue('visibility');
             const rect = element.getBoundingClientRect();
            
            const isFixed = position === 'fixed' || position === 'sticky';
            const isZIndex = zIndex >= 1000;
            const isRight = right >= 0;
            const isBottom = bottom >= 0;
            const isVisible = display !== 'none' && visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
            console.log(isFixed)
            
            if (isFixed && isZIndex && isRight && isBottom && isVisible) {
                    matchingElements.push(element);
            }
        }
        return matchingElements;
    }
    return findElementsByStyle();
    """

    try:
        elements = driver.execute_script(javascript_to_execute)
        if elements:
            print(f"Found {len(elements)} element(s) matching computed style criteria.")
            return elements
        else:
            print("No elements matched the computed style criteria.")
            return []
    except Exception as e:
        print(f"Error executing computed style search script: {e}")
        return []


def _get_html_from_element(element: WebElement, driver: WebDriver):
    """
    Provides with HTML of an element, handling iframes.
    Args:
        element:
        driver:

    Returns:
        The HTML content as a string.
    """

    wrapper_html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(wrapper_html, features="html.parser")

    iframe_tag = soup.find('iframe')
    if not iframe_tag:
        return wrapper_html

    try:
        live_iframe = element.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(live_iframe)
        iframe_html = driver.find_element(By.TAG_NAME, "html").get_attribute('outerHTML')
        driver.switch_to.default_content()
        print("  - Successfully extracted iframe HTML and switched back.")
    except Exception as e:
        print(f"  - Error switching to iframe: {e}")
        driver.switch_to.default_content()
        iframe_html = "<!-- Could not retrieve iframe content -->"

    iframe_soup = BeautifulSoup(iframe_html, features="html.parser")
    iframe_tag.clear()
    iframe_tag.append(iframe_soup)
    # print("----")
    # print(soup.text)
    # print("----")

    return soup.prettify()


def _is_element_interactive(element: WebElement):
    try:
        return element is not None and element.is_displayed() and element.is_enabled()
    except Exception:
        return False


def _find_cursor_is_pointer(container_element: WebElement, driver: WebDriver):
    """
    Finds a clickable element by recursively searching the DOM, intelligently
    prioritizing the content of iframes over their clickable parent containers.

    Args:
        container_element: The parent WebElement to search within.
        driver: The active Selenium WebDriver instance.

    Returns:
        A dictionary containing the found element and the exploration path.
    """
    javascript_to_execute = """
    // =========================================================================
    //  HELPER FUNCTIONS
    // =========================================================================

    function getXPath(node) {
        if (!node || node.nodeType !== 1) { // Only process element nodes (type 1)
            return '';
        }
        if (node === document.body) {
            return '/html/body';
        }
        if (node.id) {
            // --- THE FIX IS HERE ---
            // Changed from a template literal to standard string concatenation.
            // This is much safer when embedding JS inside a Python string.
            return '//*[@id="' + node.id + '"]';
        }

        const parent = node.parentNode;
        // Handle root elements that might not have a parent with children
        if (!parent || !parent.children) {
            return node.tagName.toLowerCase();
        }

        const siblings = Array.from(parent.children);
        const sameTagSiblings = siblings.filter(sibling => sibling.tagName === node.tagName);

        if (sameTagSiblings.length > 1) {
            // Find the 1-based index of the element among its siblings of the same tag
            const index = sameTagSiblings.indexOf(node) + 1;
            return getXPath(parent) + '/' + node.tagName.toLowerCase() + '[' + index + ']';
        } else {
            return getXPath(parent) + '/' + node.tagName.toLowerCase();
        }
    }

    function getAttributes(element) {
        if (!element.attributes) return {};
        return Array.from(element.attributes).reduce((obj, attr) => {
            obj[attr.name] = attr.value;
            return obj;
        }, {});
    }

    // =========================================================================
    //  CORE RECURSIVE FUNCTION
    // =========================================================================

    function findPointerCursorElements(startNode, maxDepth = 10, currentDepth = 0, iframeXPath = null) {
        if (!startNode || currentDepth > maxDepth) return [];

        const results = [];

        try {
            if (startNode.nodeType === 1 || startNode.nodeType === 11) { // Element or ShadowRoot

                if (startNode.nodeType === 1 && window.getComputedStyle(startNode).cursor === 'pointer') {
                    results.push({
                        tagName: startNode.tagName,
                        id: startNode.id,
                        className: startNode.className,
                        text: startNode.textContent?.trim()?.slice(0, 100) || '',
                        xpath: getXPath(startNode),
                        attributes: getAttributes(startNode),
                        iframe_xpath: iframeXPath 
                    });
                }

                const children = Array.from(startNode.children || []);
                for (const child of children) {
                    if (child.tagName === 'IFRAME') {
                        const currentIframeXPath = getXPath(child);
                        try {
                            const iframeDoc = child.contentDocument || child.contentWindow?.document;
                            if (iframeDoc?.body) {
                                results.push(...findPointerCursorElements(iframeDoc.body, maxDepth, currentDepth + 1, currentIframeXPath));
                            }
                        } catch (e) {
                            console.warn('Cannot access iframe content:', child);
                        }
                    } 
                    else if (child.shadowRoot) {
                        results.push(...findPointerCursorElements(child.shadowRoot, maxDepth, currentDepth + 1, iframeXPath));
                    }
                    else {
                        results.push(...findPointerCursorElements(child, maxDepth, currentDepth + 1, iframeXPath));
                    }
                }
            }
        } catch (e) {
            console.error('Error checking element:', startNode, e);
        }

        return results;
    }

    // =========================================================================
    //  MAIN EXECUTION
    // =========================================================================

    return findPointerCursorElements(arguments[0], 10, 0, null);
    """

    try:
        result = driver.execute_script(javascript_to_execute, container_element)
        return result

    except Exception as e:
        print(f"  - An error occurred during the recursive search script: {e}")
        return {'foundElement': None, 'exploredPath': []}
