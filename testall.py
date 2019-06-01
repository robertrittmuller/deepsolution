import sys
import time
import pathlib
import os
import os.path
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# get a list of files to process using the passed path
args = sys.argv[1:]
testpath = args[0]
testedpath = pathlib.Path(args[1])

# set the timestamp for the results folder
timestr = time.strftime("%Y%m%d-%H%M%S")

# define the path
currentDirectory = pathlib.Path(testpath)
# define the pattern
currentPattern = "net*.js"

# setup browser 
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.default_content_setting_values.automatic_downloads": 1
})
chromeOptions.add_argument(f'user-agent={user_agent}')
chromeOptions.add_argument('headless')

browser=webdriver.Chrome(options=chromeOptions)
browser.get('https://selfdrivingcars.mit.edu/deeptraffic/')
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "filePicker"))
    )
    for currentFile in currentDirectory.glob(currentPattern):  
        # create folder for this test case's results
        fileNameComponents = str(currentFile).split("-")
        currentFileName = fileNameComponents[0] + "-" + fileNameComponents[1] + "-" + fileNameComponents[2]
        # rootFileName = os.path.splitext(currentFileName)[0]
        path, rootFileName = os.path.split(currentFileName)
        testedFolderName = rootFileName + '_' + timestr
        resultsDirectory = testedpath.joinpath(str(testedFolderName))
        if not (os.path.isdir(resultsDirectory)):
            print('Creating new folder ' + str(resultsDirectory))
            resultsDirectory.mkdir()

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
        score = element.text
        score = score.replace("mph", "")
        score = score.replace(" ", "")
        if(float(score) >= 76):
            ext = '_' + score + '_FTW.js'
        else:
            ext = '_' + score + '.js'
            
        new_file_name = str(currentFile).replace('.js', str(ext))
        os.rename(currentFile, new_file_name)
        shutil.move(new_file_name, resultsDirectory)
        print('Processed - ' + str(currentFile) + ' with a score of ' + element.text[0:5])

         # click last submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

        
finally:
    browser.quit()


