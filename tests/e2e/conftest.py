import os
import pytest
from playwright.sync_api import sync_playwright

# Get frontend URL from environment variable or default to localhost:5173
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

@pytest.fixture
def browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False, slow_mo=2000)  # Set headless=False to see the browser during testing
    yield browser
    browser.close()
    p.stop()

@pytest.fixture
def page(browser):
    p = browser.new_page()
    p.set_viewport_size({"width": 1920, "height": 1080})
        # Auto-focus window
    p.evaluate("window.focus()")
    return p

@pytest.fixture
def frontend_url():
    """Provides the frontend URL to tests, configurable via FRONTEND_URL environment variable"""
    return FRONTEND_URL