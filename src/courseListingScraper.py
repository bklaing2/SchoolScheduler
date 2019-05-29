from schedule import schedule
from schedule import course
from schedule import section
from schedule import block
from schedule import location

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

# Courses
courses = [course('CSCE', 313), course('MATH', 311), course('CSCE', 481), course('ECEN', 350), course('ECEN', 314)]
courses.sort()

HONORS = True


# Other variables
try:
    with open('data/user.dat', 'r') as user_data:
        username, pwd = user_data.readlines()

    if username == 'USERNAME' or pwd == 'PASSWORD' or username == '' or pwd == '':
        raise FileNotFoundError
except FileNotFoundError:
    print('To save data, add your username and password to data/user.dat')
    username, pwd = input('Username: '), input('Password: ')

cas_title = 'Central Authentication Service'

url_cas = 'https://cas.tamu.edu/cas/login?service=https://compass-sso.tamu.edu:443/ssomanager/c/SSB?pkg=bwykfcls.p_sel_crse_search;renew=true'
url_term = 'https://compass-ssb.tamu.edu/pls/PROD/bwykfcls.p_sel_crse_search'
url_courses = 'https://compass-ssb.tamu.edu/pls/PROD/bwykgens.p_proc_term_date?deviceType=C'
url_adv_search = 'https://compass-ssb.tamu.edu/pls/PROD/bwykfcls.p_sel_crse_search_advanced?term_in=201931&SUB_BTN=Advanced+Search+'
url_sections = 'https://compass-ssb.tamu.edu/pls/PROD/bwykfcls.P_GetCrse?deviceType=C'

subjects = []
for course in courses:
    if course.subject not in subjects: subjects.append(course.subject)
subjects.sort()

course_numbers = {}
for subject in subjects:
    numbers = []
    for course in courses:
        if course.subject == subject: numbers.append(course.number)
    course_numbers[subject] = numbers


def wait_for_url(url, driver):
    while url != driver.current_url: time.sleep(.05)

def command_click(element, driver):
    ActionChains(driver).key_down(Keys.COMMAND).click(element).key_up(Keys.COMMAND).perform()

def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def create_block(loc, times, days):
    loc, times = str(loc), str(times)

    if 'WEB' in loc:
        building = 'WEB'
        room = 'N/A'
    elif 'TBA' in loc:
        building = 'TBA'
        room = 'TBA'
    else:
        building, room = loc.split()
        loc = location(building, room)

    if 'WEB' in times or 'TBA' in times: start, end = 'TBA', 'TBA'
    else: start, end = times.split('-')

    return block(start, end, list(days), loc)


def collect_sections(driver):
    scroll_down(driver)

    sections = []
    closed = False

    table = driver.find_element_by_class_name('datadisplaytable')
    rows = table.find_elements_by_tag_name('tr')
    del rows[0:2]

    # Iterate through sections
    i = 0
    while i < len(rows):
        cols = rows[i].find_elements_by_tag_name('td')

        # If new section
        if cols[3].get_attribute('innerHTML') != '&nbsp;':
            crn = int(cols[1].find_element_by_tag_name('a').get_attribute('innerHTML'))
            number = int(cols[4].find_element_by_tag_name('a').get_attribute('innerHTML'))
            seats_available = int(cols[12].get_attribute('innerHTML'))

            # Section is open
            if seats_available > 0:
                closed = False

                # Create new section
                sec = section(crn, number, seats_available)
                sec.add_block(create_block(cols[18].get_attribute('innerHTML'), cols[9].get_attribute('innerHTML'), cols[8].get_attribute('innerHTML')))

                # Add based on honors
                if HONORS: sections.append(sec)
                elif number < 200 or number >= 300: sections.append(sec)
                else: closed = True


            # Section is closed
            else: closed = True

        # Continuation of previous section
        elif not closed: sections[-1].add_block(create_block(cols[18].get_attribute('innerHTML'), cols[9].get_attribute('innerHTML'), cols[8].get_attribute('innerHTML')))
        
        i += 1
    
    return sections


# Opening Chrome in bot profile
options = webdriver.ChromeOptions() 
options.add_argument(r'user-data-dir=/Users/Bryceson/Library/Application Support/Google/Chrome/Selenium')


with webdriver.Chrome(executable_path=r'/usr/local/bin/chromedriver', options=options) as driver:
    driver.get(url_cas)

    # CAS
    form = driver.find_element_by_id('fm1')
    login = form.find_element_by_id('username')
    login.send_keys(username, Keys.RETURN)

    form = driver.find_element_by_id('fm1')
    password = form.find_element_by_id('password')
    password.send_keys(pwd, Keys.RETURN)


    # Selecting term
    wait_for_url(url_term, driver)

    submit = driver.find_elements_by_tag_name('input')[-2]
    submit.click()

    # Selecting subjects
    select = driver.find_elements_by_name('sel_subj')[1]
    options = select.find_elements_by_tag_name('OPTION')

    option_count = 0
    for option in options:
        if option.get_attribute('value') in subjects:
            command_click(option, driver)
            option_count += 1
            if option_count >= len(subjects): break

    submit = driver.find_elements_by_name('SUB_BTN')[0]
    submit.click()

    # Iterating through subject tables
    i, course_count, number_count = 0, 0, 0
    for subject in subjects:
        
        # switching to leftmost tab
        driver.switch_to.window(driver.window_handles[-1])
        wait_for_url(url_sections, driver)
        scroll_down(driver)

        table = driver.find_elements_by_class_name('datadisplaytable')[i]
        rows = table.find_elements_by_tag_name('tr')

        # Opening new tabs of desired sections
        j = 1
        for j in range(len(rows)):
            try:
                number = int(rows[j].find_elements_by_class_name('dddefault')[1].get_attribute('innerHTML'))
                submit = rows[j].find_element_by_name('SUB_BTN')
            except:
                number = -1


            if number in course_numbers[subject]:
                number_count += 1

                # Opening section in new tab
                command_click(submit, driver)
                driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])

                # Collecting sections
                wait_for_url(url_sections, driver)

                for sec in collect_sections(driver): courses[course_count].add_section(sec)
                course_count += 1

                # switching to leftmost tab
                driver.close()
                driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
                driver.refresh()
                wait_for_url(url_sections, driver)

                table = driver.find_elements_by_class_name('datadisplaytable')[i]
                rows = table.find_elements_by_tag_name('tr')
                scroll_down(driver)

                if number_count >= len(course_numbers[subject]) or course_count >= len(courses):
                    number_count = 0
                    break

        i += 1

# print('\n\nAvailable Courses:')
# for course in courses: print(str(course))

sched = schedule(courses)
print(str(sched))