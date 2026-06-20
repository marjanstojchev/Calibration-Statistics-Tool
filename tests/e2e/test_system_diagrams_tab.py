# def test_tab_launch(page):
#     page.goto('http://localhost:5173')
#     page.get_by_role("button", name="System Diagrams").click()
#     page.locator('h3:has-text("System Diagrams")').wait_for(timeout=5000)


from playwright.sync_api import expect


def test_two_slides_combo_conf1(page):
    page.goto('http://localhost:5173')
    page.get_by_role("button", name="System Diagrams").click()
    
    # Get first primGraph select
    select = page.locator('#primGraph-0')
    select.scroll_into_view_if_needed()

    assert select.is_visible()
    
    # Check initial value
    initial_value = select.input_value()
    print(f"Initial value: {initial_value}")
    
    # Use select_option() - the proper way for native <select> elements
    select.select_option('normLevel')
    
    # Verify the selection changed visually
    new_value = select.input_value()
    print(f"New value: {new_value}")
    assert new_value == 'normLevel', f"Expected 'normLevel', got '{new_value}'"
    
    # Verify the displayed option text matches
    selected_option = page.locator('#primGraph-0 option[value="normLevel"]')
    option_text = selected_option.text_content()
    print(f"Selected option text: {option_text}")
    assert 'normLevel' in option_text

# def test_two_slides_combo_conf2(page):
#     page.goto('http://localhost:5173')
#     page.get_by_role("button", name="System Diagrams").click()

#     # Get first secGraph select
#     select = page.locator('#secGraph-1')
#     select.scroll_into_view_if_needed()

#     assert select.is_visible()

#      # Check initial value
#     initial_value = select.input_value()
#     print(f"Initial value: {initial_value}")

#     # Use select_option() - the proper way for native <select> elements
#     select.select_option('diffPhaseDiff')
    
#     # Verify the selection changed visually
#     new_value = select.input_value()
#     print(f"New value: {new_value}")
#     assert new_value == 'diffPhaseDiff', f"Expected 'diffPhaseDiff', got '{new_value}'"
    
#     # Verify the displayed option text matches
#     selected_option = page.locator('#secGraph-1 option[value="diffPhaseDiff"]')
#     option_text = selected_option.text_content()
#     print(f"Selected option text: {option_text}")
#     assert 'diffPhaseDiff' in option_text

def test_two_plot_setup_inputs(page):
    page.goto('http://localhost:5173')
    page.get_by_role("button", name="System Diagrams").click()

    az_input = page.locator('#az')
    el_input = page.locator('#el') 

    az_value = "90"
    az_input.fill(az_value)
    assert az_input.input_value() == az_value

    el_value = "45"
    el_input.fill(el_value)
    assert el_input.input_value() == el_value
