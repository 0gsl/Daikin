from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

def main():
    print("Starting browser...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    # Initialize Chrome driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Create WebDriverWait object
    wait = WebDriverWait(driver, 30)
    
    try:
        # Step 1: Navigate to Daikin website
        print("Opening Daikin website...")
        driver.get("https://daikinapplied.com/")
        time.sleep(5)
        
        # Step 2: Click Careers link
        print("Clicking Careers link...")
        careers_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/careers']"))
        )
        careers_link.click()
        time.sleep(3)
        
        # Step 3: Click Browse All Jobs button
        print("Clicking Browse All Jobs button...")
        browse_jobs_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 
                "a.btn[href='https://myjobs.adp.com/daikinappliedcareers/cx']"))
        )
        browse_jobs_button.click()
        
        # Wait for ADP page to load
        print("Waiting for ADP page to load...")
        time.sleep(15)
        
        # Wait for and find the search field using JavaScript to access shadow DOM
        print("Looking for search field...")
        search_field = None
        for _ in range(20):  # Try for about 20 seconds
            search_field = driver.execute_script("""
                const searchComponent = document.querySelector('#cx-job-search');
                if (!searchComponent) {
                    console.log('Search component not found');
                    return null;
                }
                
                const shadowRoot = searchComponent.shadowRoot;
                if (!shadowRoot) {
                    console.log('Shadow root not found');
                    return null;
                }
                
                // Try to find the sdf-input first
                const sdfInput = shadowRoot.querySelector('sdf-input');
                if (sdfInput && sdfInput.shadowRoot) {
                    const input = sdfInput.shadowRoot.querySelector('input');
                    if (input) return input;
                }
                
                // Fallback to other selectors
                return shadowRoot.querySelector('input[type="text"]') ||
                       shadowRoot.querySelector('input');
            """)
            
            if search_field:
                print("Found search field!")
                break
                
            print("Waiting for search field to initialize...")
            time.sleep(1)
            
        if not search_field:
            raise Exception("Could not find search field")
            
        # Enter search term
        print("Entering search term 'QA'...")
        driver.execute_script("""
            arguments[0].value = 'QA';
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, search_field)
        time.sleep(3)  # Give more time for the input to register
        
        # Find and click the search button
        print("Looking for search button...")
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.vdl-button--primary"))
        )
        print("Clicking search button...")
        search_button.click()
        # After clicking search button...
        time.sleep(5)  # Wait for search to initiate
        
        # Wait for job listing page to load
        print("Waiting for job listing page...")
        expected_url = "https://myjobs.adp.com/daikinappliedcareers/cx/job-listing?keyword=qa"
        
        start_time = time.time()
        timeout = 30  # 30 seconds timeout
        
        while time.time() - start_time < timeout:
            current_url = driver.current_url.lower()
            print(f"Current URL: {current_url}")  # Debug print
            
            if "job-listing" in current_url and "keyword=qa" in current_url:
                print(f"Successfully loaded job listing page: {current_url}")
                print("Displaying page for 10 seconds before timeout...")
                time.sleep(10)
                print("Test completed successfully")
                return
            
            time.sleep(1)
        
        print(f"Timed out waiting for job listing page. Current URL: {driver.current_url}")
        return
        
        # Display the job listing for 15 seconds
        print("Displaying job listing for 15 seconds...")
        time.sleep(15)
        
        # Find and click the Apply button
        print("Clicking Apply button...")
        apply_button_xpath = """/html/body/cx-root/div/div/cx-shell/cx-header/div[2]/cx-careersite-bbq/div/cx-root/div/cx-job-listing/section/div/div[1]/cx-reqs-list/div/div/div/div/div/div/div[2]/adp-selection-list/adp-list-view[1]/div/div/div/div/div/div/div[2]/adp-button/div/button"""
        
        apply_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, apply_button_xpath))
        )
        apply_button.click()
        
        # Wait for auth page to load
        print("Waiting for auth page...")
        for _ in range(30):  # Try for 30 seconds
            if "auth" in driver.current_url:
                print("Auth page loaded. Test complete.")
                break
            time.sleep(1)
        else:
            print(f"Failed to reach auth page. Current URL: {driver.current_url}")
            raise Exception("Auth page not loaded")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        driver.save_screenshot("error_screenshot.png")
        
        # Print shadow DOM info for debugging
        shadow_info = driver.execute_script("""
            const searchComps = document.querySelectorAll('sdf-search');
            return Array.from(searchComps).map(comp => ({
                id: comp.id,
                hasRoot: !!comp.shadowRoot,
                html: comp.outerHTML
            }));
        """)
        print("\nSearch components found:")
        print(shadow_info)
        
        raise
        
    finally:
        print("Closing browser...")
        driver.quit()
        
    print("Test completed!")

if __name__ == "__main__":
    main()