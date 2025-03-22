# Define the __all__ variable
print('importo')
__all__ = ["structeasy_class", "structeasy_lib"]
# Import the submodules
from . import structeasy_class
from . import structeasy_lib
