__version__ = "0.1.0"


from .launcher import launch_page, check_ip
from ._detector_utils import _find_elements_by_computed_style, _get_html_from_element
from ._launcher_utils import _handle_cookie_consent

print(f"BotScout package initialized (version {__version__})")
