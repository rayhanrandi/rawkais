import sys
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


LOGIN_URL = "https://academic.ui.ac.id/main/Authentication/"
LOGOUT_URL = "https://academic.ui.ac.id/main/Authentication/Logout"
HOME_URL = "https://academic.ui.ac.id/main/Welcome/"
# IRS_URL = "https://academic.ui.ac.id/main/CoursePlan/CoursePlanEdit"


def execute() -> None:
    """
    executes script, checks if login page is loaded.
    if its loaded, then autologin.
    """
    global tries

    loaded = check_page_load('login')
    if loaded: 
        login(USERNAME, PASSWORD)


def login(username: str, password: str) -> None:
    """
    autofills username and password, then submits.
    checks if the home page is fully loaded, indicating login successful.
    checks if the term is correct, if yes, then proceed to irs page.
    if not, flow is passed into logout function to relogin.
    """
    global tries

    tries += 1

    uname_field = driver.find_element(By.NAME, 'u')
    uname_field.clear()
    uname_field.send_keys(username)

    pw_field = driver.find_element(By.NAME, 'p')
    pw_field.clear()
    pw_field.send_keys(password)

    driver.find_element(By.XPATH, 
                        './/*[@id="submit"]/input[@type="submit"]').click()
    
    check_page_load('home')
    print(f'\n[{tries}] >> Succesfully logged in...')
    
    active_term = driver.find_element(
        By.XPATH, 
        '//*[@id="m_b1"]/div[1]').get_attribute('innerText')
    
    print(f'[{tries}] >> Current status:\n' + '=' * 75 + f'\n{active_term}\n' + '=' * 75)

    if (f'Term {TERM}' not in active_term):
        print(f'[{tries}] >> Term incorrect. retrying...')
        logout()

    print('>> Term correct!')

    isi_irs(IRS)


def isi_irs(irs: dict) -> None:
    """
    opens irs page then check if page successfully loaded,
    if yes then autofill classes according to dict then submits.
    -> key = class code, value: priority list
    """
    global tries

    driver.get(IRS_URL)
    check_page_load('irs')
    print(f'[{tries}] >> Filling in classes...')
    print(f'[{tries}] >> Selected:')

    # pick class w priority
    for matkul in list(irs.keys()):
        selection = driver.find_elements(By.NAME, matkul)
        # handle priority lists
        pick_class(selection, irs[matkul])

    ## 4. submit irs
    # driver.find_element(
    #     By.XPATH, '//*[@id="ti_m1"]/div/table/tbody/tr/td/form/div[2]/input[2]'
    #     ).click()
    
    print('done. ' * 10)
    print('done. ' * 10)
    print('done. ' * 10)
    print(f'in {tries} tries.')


def logout() -> None:
    """
    redirects to login page should logout succeeds.
    then run execute function again,
    starting the proccess from the beginning (relogin).
    """
    global tries

    driver.get(LOGOUT_URL)
    execute()


def pick_class(selection: list, priority: list) -> None:
    """
    function receives current class selection 
    and its list of priorities as arguments.
    then loops through the priorities to check if
    the capacity is enough for user to enroll.
    if yes, then enrolls the user to the class.
    if not, then checks the following priorty in the list.
    """
    global tries

    for p in priority:
        selected_class = selection[p]
        class_name = selected_class.find_element(
            By.XPATH, '..').find_element(
            By.XPATH, 'following-sibling::*[1]').find_element(
            By.XPATH, './/*[not(preceding-sibling::*)]').find_element(
            By.XPATH, './/*[not(preceding-sibling::*)]').get_attribute('innerText')
        capacity = selected_class.find_element(
            By.XPATH, '..').find_element(
            By.XPATH, 'following-sibling::*[3]')
        enrolled = capacity.find_element(By.XPATH, 'following-sibling::*[1]')
        if (int(capacity.get_attribute("innerText")) > int(enrolled.get_attribute("innerText"))):
            if not (selection[p].is_selected()):
                selected_class.click()
                print(f' - {class_name} -> capacity: {capacity.get_attribute("innerText")}, current: {enrolled.get_attribute("innerText")}')
                break
        

def check_page_load(page: str) -> bool:
    """
    takes a string of page that is checked as argument,
    then checks if the page is loaded successfully
    by checking if certain elements are present in the page
    according to the argument.
    if not present, wait for <REFRESH_RATE> second to load 
    then throw exception to reload and check again recursively
    if present, then return true.
    """
    global tries

    try:
        if (page == 'login'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="u"]'))
            WebDriverWait(driver, REFRESH_RATE).until(data)
        elif (page == 'home'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="m_b1"]/div[1]'))
            WebDriverWait(driver, REFRESH_RATE).until(data)
        elif (page == 'irs'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="ti_h"]'))
            WebDriverWait(driver, REFRESH_RATE).until(data)
    except TimeoutException as e:
        print(f'[{tries}] >> Heavy load. refreshing...')
        if (page == 'login'):
            driver.get(LOGIN_URL)
        elif (page == 'home'):
            driver.get(HOME_URL)
        elif (page == 'irs'):
            driver.get(IRS_URL)
        # handle_alerts()
        check_page_load(page)

    return True


def handle_alerts() -> None:
    """
    helper function to handle any alerts that might pop up
    by focusing into the alert and autoclicks accept to dismiss.
    """
    global tries

    try:
        WebDriverWait(driver, REFRESH_RATE).until(EC.alert_is_present)
        driver.switch_to.alert.accept()
    except:
        pass

    

if __name__ == "__main__":

    config = json.load(open('./config.json'))

    USERNAME = config['username']
    PASSWORD = config['password']

    """
    Term selection:
    1 : smt-ganjil, 2 : smt-genap, 3: smt-pendek
    """
    TERM = config['term']

    """
    valid format -> key value pairs of <str: list[int]>,
    'c[<class_code>_<curriculum_code>]': [<priority>]
    with 0 being the topmost class 
    e.g. A class = 0, B class = 1, etc.
    """
    IRS = config['irs']
    
    options = webdriver.ChromeOptions()

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('log-level=3')
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless=new")  # uncomment to disable chrome window

    # Pass the argument 1 to allow and 2 to block
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 2}
    )
    options.add_experimental_option('detach', True) # keep browser open
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # open browser
    driver = webdriver.Chrome(options=options)
    # driver.set_page_load_timeout(1)
    REFRESH_RATE = 1

    ### 3. TEST isi irs: comment ###
    IRS_URL = "file:///C:/Users/rayha/Dokumen/code/projects/autoirs/Pengisian%20IRS%20-%20Rayhan%20Putra%20Randi%20(2106705644)%3B%20Kurikulum%2001.00.12.01-2020%20-%20SIAK%20NG.html"
    # driver.get(IRS_URL)
    # isi_irs(IRS)

    tries = 1

    # driver
    while True:
        driver.get(LOGIN_URL)
        execute()
        sys.exit(0) # ends instance if ran successfully
    