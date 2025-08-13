# test_mpo_model.py
# Test mpo_model

"""
This module tests the mpo_model.py file using pytest. It checks if classes like Prayer and Category are created
correctly, handle invalid inputs with errors, and maintain proper attributes. Fixtures create reusable test objects,
and assertions verify expected behavior. As a learner, tests like these help ensure your code works as intended and
catch bugs early.
"""

import pytest
from datetime import date
from mpo_model import Prayer, Category, ModelError


@pytest.fixture
def valid_prayer():
    """
    Create a valid Prayer instance for testing.

    Returns:
        Prayer: A Prayer object with default valid values.
    """
    return Prayer(prayer="Test prayer", category="Other")


def test_prayer_constructor_valid_input(valid_prayer):
    """
    Test Prayer constructor with valid input initializes attributes correctly.

    Args:
        valid_prayer (Prayer): A valid Prayer object from the fixture.

    Verifies that all attributes (text, category, dates, etc.) are set as expected.
    """
    prayer_text = "Test prayer"
    category = "Other"
    prayer = valid_prayer
    assert prayer.prayer == prayer_text
    assert prayer.category == category
    assert prayer.create_date == date.today().strftime("%d-%b-%Y")
    assert prayer.answer_date is None
    assert prayer.answer is None
    assert prayer.display_count == 0


def test_prayer_constructor_empty_prayer():
    """
    Test Prayer constructor raises ModelError for empty prayer text.

    Ensures the constructor catches invalid (empty) prayer text.
    """
    with pytest.raises(ModelError, match="Prayer text cannot be empty"):
        Prayer(prayer="", category="Other")


def test_prayer_constructor_invalid_category():
    """
    Test Prayer constructor raises ModelError for invalid category.

    Checks that an invalid category name triggers the expected error.
    """
    with pytest.raises(ModelError, match="Invalid category"):
        Prayer(prayer="Test prayer", category="Invalid")


def test_category_constructor():
    """
    Test Category constructor initializes attributes correctly.

    Verifies that the category name and display count are set properly.
    """
    category = Category(category="Praise")
    assert category.category == "Praise"
    assert category.category_display_count == 0