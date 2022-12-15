'''
Purpose: main module for testing using pytest
'''

# Standard library imports
#import sys
#import pytest

# Third party imports


# Local application imports
# from local_module import local_class
# from local_package import local_function
# from package(directory).module import function
from ..my_prayers_pkg import welcome, honor_God, my_concerns, Gods_will
#from .my_prayers_pkg import *


def test_main():
    assert welcome.display_msg() == "welcome"               # module_filename.function
    assert honor_God.display_msg() == "honor_God"
    assert my_concerns.manage_prayers() == "my_concerns"
    assert Gods_will.display_msg() == "Gods_will"


if __name__ == "__main__":
    test_main()

