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
from selenium.common.exceptions import NoSuchElementException

# get a list of files to process using the passed path
args = sys.argv[1:]

# define the paths
testDirectory = pathlib.Path(args[0])
testedDirectory = pathlib.Path(args[1])
downloadDirectory = pathlib.Path(args[2])

# define name to use for folder structure later on
testedFolderName = ''

# define the pattern to use for finding files in the download directory
currentPattern = "*.js"

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

# run test cases -------------------------------------------------------------------------------------------
try:
# Start running test cases
    for currentTestCase in testDirectory.glob(currentPattern):
        # Load up the browser each time to minimize memory leak issues
        print('Starting test case...')
        browser=webdriver.Chrome(options=chromeOptions)
        browser.implicitly_wait(0)

        # Just in case we are running in headless mode set up file downloads
        browser.command_executor._commands["send_command"] = (
            "POST",
            '/session/$sessionId/chromium/send_command'
        )
        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': str(downloadDirectory)
            }
        }
        browser.execute("send_command", params)

        time.sleep(5)

        # Load up DeepTraffic
        browser.get('https://selfdrivingcars.mit.edu/deeptraffic/')

        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "filePicker"))
        )

        # create folder for this test case's results
        timestr = time.strftime("%Y%m%d-%H%M%S")
        currentFileName = currentTestCase.stem
        rootFileName = os.path.splitext(currentFileName)[0]
        testedFolderName = rootFileName + '_' + timestr
        print('Working on test case ' + str(testedFolderName))
        resultsDirectory = testedDirectory.joinpath(str(testedFolderName))
        resultsDirectory.mkdir()

        # Upload the test case
        fileinput = browser.find_element_by_id('filePicker')
        fileinput.send_keys(str(currentTestCase))

        time.sleep(5)

        # click first submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

        # click second submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

         # start the test case run (training)
        eval_button = browser.find_elements_by_xpath('//*[@id="trainButton"]')[0]
        eval_button.click()

        # wait until the test case training ends
        while True:
            try:
                popup = browser.find_element_by_xpath("/html/body/div[3]")
                if popup.is_displayed():
                   break
            except NoSuchElementException:
                continue

        time.sleep(5)

        # click last submit button
        submit_button = browser.find_elements_by_xpath('/html/body/div[3]/div[7]/div/button')[0]
        submit_button.click()

        time.sleep(5)

        # start processing the test case outputs -------------------------------------------------------------------
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "filePicker"))
            )
            for currentFile in downloadDirectory.glob(currentPattern):  

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
            print('Evaluation Run Completed!')
    
        browser.quit()

finally:
    print('Test case runs completed!')




