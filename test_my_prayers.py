from io import StringIO
import sys
import pytest
import welcome, honor_God, my_concerns, Gods_will


def test_main():
    assert welcome.display_msg() == "welcome"               # module_filename.function
    assert honor_God.display_msg() == "honor_God"
    assert my_concerns.manage_prayers() == "my_concerns"
    assert Gods_will.display_msg() == "Gods_will"


if __name__ == "__main__":
    test_main()

