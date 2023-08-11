from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import sys


def execute():
    """
    executes script, checks if login page is loaded.
    if its loaded, then autologin.
    """
    loaded = check_page_load('login')
    if (loaded): 
        login(username, password)

def login(username: str, password: str):
    """
    autofills username and password, then submits.
    checks if the home page is fully loaded, indicating login successful.
    checks if the term is correct, if yes, then proceed to irs page.
    if not, flow is passed into logout function to relogin.
    """
    uname_field = driver.find_element(By.NAME, 'u')
    uname_field.clear()
    uname_field.send_keys(username)

    pw_field = driver.find_element(By.NAME, 'p')
    pw_field.clear()
    pw_field.send_keys(password)

    driver.find_element(By.XPATH, 
                        './/*[@id="submit"]/input[@type="submit"]').click()
    
    check_page_load('home')
    print('succesfully logged in...')
    
    active_term = driver.find_element(
        By.XPATH, 
        '//*[@id="m_b1"]/div[1]').get_attribute('innerText')
    
    print(f'Current status:\n{active_term}')

    if (f'Term {term}' not in active_term):
        print('term incorrect. retrying...')
        logout()

    isi_irs(irs)

def isi_irs(irs: dict):
    """
    opens irs page then check if page successfully loaded,
    if yes then autofill classes according to dict then submits.
    -> key = class code, value: priority list
    """
    driver.get(irs_url)
    check_page_load('irs')
    print('filling in classes...')
    print('selected:')

    # pick class w priority
    for matkul in list(irs.keys()):
        selection = driver.find_elements(By.NAME, matkul)
        # handle priority lists
        pick_class(selection, irs[matkul])

    # 4. submit irs
    # driver.find_element(
    #     By.XPATH, '//*[@id="ti_m1"]/div/table/tbody/tr/td/form/div[2]/input[2]'
    #     ).click()
    
    print('done.')


def logout():
    """
    redirects to login page should logout succeeds.
    then run execute function again,
    starting the proccess from the beginning (relogin).
    """
    driver.get(logout_url)
    execute()

def pick_class(selection: list, priority: list):
    """
    function receives current class selection 
    and its list of priorities as arguments.
    then loops through the priorities to check if
    the capacity is enough for user to enroll.
    if yes, then enrolls the user to the class.
    if not, then checks the following priorty in the list.
    """
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
            selected_class.click()
            print(f'{class_name} -> capacity: {capacity.get_attribute("innerText")}, current: {enrolled.get_attribute("innerText")}')
            break
        
def check_page_load(page: str) -> bool:
    """
    *UNTESTED*
    takes a string of page that is checked as argument,
    then checks if the page is loaded successfully
    by checking if certain elements are present in the page
    according to the argument.
    if not present, wait for 1 second to load 
    then throw exception to reload and check again recursively
    if present, then return true.
    """
    try:
        if (page == 'login'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="u"]'))
            WebDriverWait(driver, 1).until(data)
        elif (page == 'home'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="m_b1"]/div[1]'))
            WebDriverWait(driver, 1).until(data)
        elif (page == 'irs'):
            data = EC.presence_of_element_located(
                (By.XPATH, '//*[@id="ti_h"]'))
            WebDriverWait(driver, 1).until(data)
    except TimeoutException as e:
        print('heavy load. refreshing...')
        driver.refresh()
        handle_alerts()
        check_page_load(page)

    return True

def handle_alerts():
    """
    helper function to handle any alerts that might pop up
    by focusing into the alert and autoclicks accept to dismiss.
    """
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present)
        driver.switch_to.alert.accept()
    except:
        pass

    
if __name__ == "__main__":

    username = "<username>"
    password = "<password>"
    term = 2    # 1 : smt-ganjil, 2 : smt-genap, 3: smt-pendek


    """
    valid format:
    'c[<class_code>_<curriculum_code>]': [<priority>]
    with 0 begin the topmost class 
    e.g. A class = 0, B class = 1, etc.
    """
    irs = {
        'c[CSGE602012_01.00.12.01-2020]': [1,2,0,3,4],   
        'c[CSGE602091_01.00.12.01-2020]': [0,3,2,1,4,5], 
        'c[CSGE602022_01.00.12.01-2020]': [3,4,0,1,2,5], 
        'c[CSCM602055_01.00.12.01-2020]': [1,2,0],       
        'c[CSGE602040_01.00.12.01-2020]': [5,1,0,3,4,2],         
    }


    login_url = "https://academic.ui.ac.id/main/Authentication/"
    logout_url = "https://academic.ui.ac.id/main/Authentication/Logout"
    home_url = "https://academic.ui.ac.id/main/Welcome/"
    # irs_url = "https://academic.ui.ac.id/main/CoursePlan/CoursePlanEdit"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('log-level=3')
    options.add_experimental_option('detach', True) # keep browser open

    # open browser
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(1.5)

    ### 3. TEST isi irs: comment ###
    irs_url = "file:///C:/Users/rayha/Dokumen/code/projects/siakwarbot/Pengisian%20IRS%20-%20Rayhan%20Putra%20Randi%20(2106705644)%3B%20Kurikulum%2001.00.12.01-2020%20-%20SIAK%20NG.html"
    driver.get(irs_url)
    isi_irs(irs)

    # driver
    # while True:
    #     driver.get(login_url)
    #     execute()
    #     sys.exit(0) # ends instance if ran successfully
    