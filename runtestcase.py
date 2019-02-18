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

# define the paths
testDirectory = pathlib.Path(args[0])
testedDirectory = pathlib.Path(args[1])
downloadDirectory = pathlib.Path(args[2])

# define name to use for folder structure later on
testedFolderName = ''

# define the pattern to use for finding files in the download directory
currentPattern = "*.js"

# setup browser 
browser=webdriver.Chrome()
browser.get('https://selfdrivingcars.mit.edu/deeptraffic/')

# run test cases -------------------------------------------------------------------------------------------
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "filePicker"))
    )

    for currentTestCase in testDirectory.glob(currentPattern):

        # create folder for this test case's results
        timestr = time.strftime("%Y%m%d-%H%M%S")
        currentFileName = currentTestCase.stem
        rootFileName = os.path.splitext(currentFileName)[0]
        testedFolderName = rootFileName + '_' + timestr
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
        element = WebDriverWait(browser, 14420).until(
            EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[3]/h2"),'Training finished!')
        )


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
                ext = '_' + element.text[0:5] + '.js'
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

finally:
    print('Test case runs completed!')
    browser.quit()




