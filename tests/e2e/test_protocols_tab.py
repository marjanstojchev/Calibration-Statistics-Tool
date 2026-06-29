protocol_file_path = 'C:\\Calibration Statistics Tool\\measurement_data\\protocol_files\\2024-01-15_12-30-45_Tuner1_rf12345_dsp67890_Seq1_TxAnt1_Diagram1_Protocol.txt'  # Update with actual test file path
ptu2_file_path = 'C:\\Calibration Statistics Tool\\measurement_data\\ptu_files\\2024-01-15_08-15-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt0_Diagram0_Az_ptu2.txt'  # Update with actual test file path
def test_protocols_input(page, frontend_url):
    page.goto(frontend_url)
    loadprot_btn = page.locator('#proto-input')

    # loadprot_btn.click()
    loadprot_btn.set_input_files(protocol_file_path)

    # Verify badge appears with file count
    badge = page.locator('.badge-info:has-text("protocol files")')
    assert badge.is_visible()
    assert '1 protocol files' in badge.text_content()  # or whatever count

def test_multiple_checkboxes(page, frontend_url):
    page.goto(frontend_url)
    
    expected = {
        "Search PTU2 Files": True,    # should be checked
        "Search TxAnt. Diag. Files": False,    # should be checked
        "Latest Protocol": False,    # should be checked
        'Burnin Start': False,    # should be checked
        'EOL Error(s)': False,    # should be checked
        'EOL Abort Criterion(s)': True,    # should be checked
        'EOL Meas. Limits Exceeded': True,    # should be checked
    }
    
    for label, should_be_checked in expected.items():
        checkbox = page.locator(f'label:has-text("{label}") input')
        assert checkbox.is_checked() == should_be_checked
        checkbox.click()  # verify toggle


def test_protocol_type_radio(page, frontend_url):

    page.goto(frontend_url)
    page.get_by_role("radio", name="Auto Recognition").click()
    assert page.get_by_role("radio", name="Auto Recognition").is_checked()

    page.get_by_role("radio", name="BurnIn").click()
    assert page.get_by_role("radio", name="BurnIn").is_checked()

    page.get_by_role("radio", name="Calibration").click()
    assert page.get_by_role("radio", name="Calibration").is_checked()

def test_protocol_add_ptu2_files(page, frontend_url):

    page.goto(frontend_url)
    page.get_by_text("Add PTU2 Files").click()

    file_input = page.locator('#ptu2-input')
    file_input.set_input_files(ptu2_file_path)

        # Verify
    badge = page.locator('.badge-success:has-text("PTU2")')
    assert badge.is_visible()
    assert '1 PTU2' in badge.text_content()  # or whatever count