__version__ = "0.1.0"


from .launcher import launch_page, check_ip
from ._detector_utils import _find_elements_by_computed_style, _get_html_from_element, _is_element_interactive, \
    _find_cursor_is_pointer
from ._launcher_utils import _handle_cookie_consent, _click_element_from_data

print(f"BotScout package initialized (version {__version__})")
