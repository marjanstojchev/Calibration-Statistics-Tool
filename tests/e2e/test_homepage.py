def test_page_loads(page):
    page.goto('http://localhost:5174')
    assert page.title() != ''  # Title exists

def test_heading_present(page):
    page.goto('http://localhost:5174')
    title = page.locator('.app-title')
    assert 'Calibration Statistics Tool' in title.text_content()

def test_navigate_to_limits_tab_class_name(page):
    page.goto('http://localhost:5174')
    
    # Click "Limits" button
    limits_btn = page.locator('button:has-text("Limits")')
    limits_btn.click()
    
    # Verify button is now active (has 'active' class)
    assert 'active' in limits_btn.get_attribute('class')

def test_navigate_to_limits_tab_text(page):
    page.goto('http://localhost:5174')
    limits_btn = page.locator('button:has-text("Limits")')
    limits_btn.click()
    
    # Wait for Limits tab content (specific h3 that only appears in Limits tab)
    page.locator('h3:has-text("Limits Configuration")').wait_for(timeout=5000)