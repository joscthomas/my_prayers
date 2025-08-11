# test_mpo_model
# Test mpo_model

import pytest
from datetime import date
from ..src.mpo_model import Prayer, Category, ModelError

@pytest.fixture
def valid_prayer():
    """Fixture to create a valid Prayer instance."""
    return Prayer(prayer="Test prayer", category="Other")

def test_prayer_constructor_valid_input(valid_prayer):
    """Test Prayer constructor with valid input initializes attributes correctly."""
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
    """Test Prayer constructor raises ModelError for empty prayer text."""
    with pytest.raises(ModelError, match="Prayer text cannot be empty"):
        Prayer(prayer="", category="Other")

def test_prayer_constructor_invalid_category():
    """Test Prayer constructor raises ModelError for invalid category."""
    with pytest.raises(ModelError, match="Invalid category"):
        Prayer(prayer="Test prayer", category="Invalid")

def test_category_constructor():
    """Test Category constructor initializes attributes correctly."""
    category = Category(name="Praise")
    assert category.name == "Praise"
    assert category.category_count == 0