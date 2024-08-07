from selenium.webdriver.chrome.options import Options
from selenium import webdriver  # Import from seleniumwire
import time
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

def extract_main_value(html_string):
    """
    Extract the main text value from a given HTML-like string.
    
    Args:
        html_string (str): The input string containing HTML-like tags.
    
    Returns:
        str: The main text value extracted from the HTML-like string.
    """
    # Parse the HTML string with BeautifulSoup
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Extract all text from the parsed HTML
    text = soup.get_text(separator=' ', strip=True)
    
    return text

# Specify the path to your JSON file
file_path = 'daad_data.json'
base_url = 'https://www2.daad.de'

def open_chrome(target_url):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Optional: Start browser maximized
    # chrome_options.add_argument("--headless")  # Optional: Run headless if you don't need a GUI
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")  # Only show errors

    driver = webdriver.Chrome(
        options=chrome_options
    )

    # Navigate to the target URL
    driver.get(target_url)
    time.sleep(2)
    return driver

def remove_Element(driver, className):
    banner = driver.find_element(By.CLASS_NAME, className)
    if banner is not None:
        driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", banner)

def remove_newlines(s):
    """
    Remove all newline characters from the given string.
    
    Args:
        s (str): The input string from which newline characters will be removed.
    
    Returns:
        str: The input string with all newline characters removed.
    """
    return s.replace('\n', '')

def click_on_element(driver, date_filter):
    actions = ActionChains(driver)
    actions.move_to_element(date_filter).perform()
    actions.click().perform()

def scrap_table(driver):
    row_columnData = driver.find_elements(By.CLASS_NAME, "c-description-list__content")
    tab_columns = driver.find_elements(By.CLASS_NAME, "c-detail-nav__tab")
    main_map = {}
    for column in tab_columns:
        click_on_element(driver, column)
        dict_Map = {}
        key, value = None, None
        for data in row_columnData:
            inner_html = data.get_attribute('innerHTML')
            inner_html = remove_newlines(inner_html).strip()
            if key is None:
                key = inner_html
            else:
                dict_Map[key] = inner_html
                key = None
        columnName = column.get_attribute('innerHTML')
        columnName = remove_newlines(columnName).strip()
        main_map[columnName] = dict_Map
    return main_map

def getMainElementFromClass(driver, className):
    name = driver.find_element(className)
    inner_html = name.get_attribute('innerHTML')
    inner_html = remove_newlines(inner_html).strip()
    return inner_html

def scrap_Contact_Details(driver):
    name = getMainElementFromClass(driver, "c-contact__asp")
    return {"name": name}

def scrapData(url, path_name):
    driver = open_chrome(target_url=url)
    remove_Element(driver=driver, className="qa-cookie-consent")
    remove_Element(driver=driver, className="snoop-modal-backdrop")
    remove_Element(driver=driver, className="snoop-modal-wrapper")
    table = driver.find_element(By.CLASS_NAME, "c-detail-nav")
    html_content = table.get_attribute('outerHTML')
    tables_data = scrap_table(driver=driver)
    # contactInfo = scrap_Contact_Details(driver)
    
    driver.quit()
    with open("./UniGermanData/" + path_name + ".html", 'w', encoding='utf-8') as file:
        file.write(html_content)
    return tables_data

# Open the file and load its content
with open(file_path, 'r') as file:
    datas = json.load(file)
    all_data = []
    for data in datas['courses']:
        path_name = str(data['id'])  # Use the course ID as the path name
        course_data = scrapData(base_url + data['link'], path_name)
        all_data.append({
            "id": data["id"],
            "academy": data["academy"],
            "link": data["link"],
            "data": course_data
        })

# Save all data to a single JSON file
with open('all_scraped_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(all_data, outfile, ensure_ascii=False, indent=4)