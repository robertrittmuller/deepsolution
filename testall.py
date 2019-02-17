import sys
import time
import pathlib
import os
import os.path
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# get a list of files to process using the passed path
args = sys.argv[1:]
testpath = args[0]
testedpath = args[1]

# define the path
currentDirectory = pathlib.Path(testpath)
# define the pattern
currentPattern = "*.js"

# setup browser 
browser=webdriver.Chrome()
browser.get('https://selfdrivingcars.mit.edu/deeptraffic/')
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "filePicker"))
    )
    for currentFile in currentDirectory.glob(currentPattern):  

        # Upload the file to test
        fileinput = browser.find_element_by_id('filePicker')
        fileinput.send_keys(str(currentFile))

        time.sleep(5)

        # click first submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

        # click second submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

         # start the evaluation run
        eval_button = browser.find_elements_by_xpath('//*[@id="evalButton"]')[0]
        eval_button.click()

        # wait until the evaluation ends
        element = WebDriverWait(browser, 420).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/p/b"))
        )

        # grab the score
        element=browser.find_element_by_xpath('/html/body/div[3]/p/b')
        ext = '_' + element.text[0:5] + '.js'
        new_file_name = str(currentFile).replace('.js', str(ext))
        os.rename(currentFile, new_file_name)
        shutil.move(new_file_name, testedpath)
        print('Processed - ' + str(currentFile) + ' with a score of ' + element.text[0:5])

         # click last submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

        
finally:
    browser.quit()


