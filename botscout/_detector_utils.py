

def find_elements_by_computed_style(driver):
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
            const isRight = right > 0;
            const isBottom = bottom > 0;
            const isVisible = display !== 'none' && visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
            
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
