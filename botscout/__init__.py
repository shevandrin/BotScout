__version__ = "0.1.0"


from .launcher import launch_page, check_ip
from ._detector_utils import find_elements_by_computed_style

print(f"BotScout package initialized (version {__version__})")
