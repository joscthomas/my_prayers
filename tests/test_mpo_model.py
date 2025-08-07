# test_mpo_model.py
# Tests mpo_model

import pytest
from datetime import date
from ..mpo_model import Prayer, ModelError


def test_prayer_constructor_valid_input():
    """Test Prayer constructor with valid input initializes attributes correctly."""
    prayer_text = "Test prayer"
    category = "Personal"
    prayer = Prayer(prayer=prayer_text, category=category)

    assert prayer.prayer == prayer_text
    assert prayer.category == category
    assert prayer.create_date == date.today().strftime("%d-%b-%Y")
    assert prayer.answer_date is None
    assert prayer.answer is None
    assert prayer.display_count == 0