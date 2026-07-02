def test_page_loads(page, frontend_url):
    page.goto(frontend_url)
    assert page.title() != ''  # Title exists

def test_heading_present(page, frontend_url):
    page.goto(frontend_url)
    title = page.locator('.app-title')
    assert 'Calibration Statistics Tool' in title.text_content()

def test_navigate_to_limits_tab_class_name(page, frontend_url):
    page.goto(frontend_url)
    
    # Click "Limits" button
    limits_btn = page.locator('button:has-text("Limits")')
    limits_btn.click()
    
    # Verify button is now active (has 'active' class)
    assert 'active' in limits_btn.get_attribute('class')

def test_navigate_to_limits_tab_text(page, frontend_url):
    page.goto(frontend_url)
    limits_btn = page.locator('button:has-text("Limits")')

    limits_btn.click()
    
    # Wait for Limits tab content (specific h3 that only appears in Limits tab)
    page.locator('h3:has-text("Limits FAIL")').wait_for(timeout=5000)
    #page.locator('h3:has-text("Limits Configuration")').wait_for(timeout=5000)


def test_navigate_to_limits_tab_text_fail_case(page, frontend_url):
    page.goto(frontend_url)
    limits_btn = page.locator('button:has-text("Limits")')

    limits_btn.click()
    
    # Wait for Limits tab content (specific h3 that only appears in Limits tab)
    page.locator('h3:has-text("Limits FAIL")').wait_for(timeout=5000)
