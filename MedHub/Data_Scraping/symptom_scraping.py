import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import string
import re
import csv

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_extension('uBlock-Origin_v1.12.0.crx')
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options = chromeOptions)


letters = string.ascii_lowercase

symptom_set = set()
for letter in letters:
    driver.get('http://www.mayoclinic.org/symptoms/index?letter=%s' % letter)
    symptom_links = driver.find_elements_by_xpath('//*[@id="index"]/ol/li')
    for el in symptom_links:
        symptom = el.text
        symptom_see = re.findall('(?<=\(See: ).+(?=\)$)', symptom)
        print symptom_see
        if symptom_see:
            symptom_set.add(symptom_see[0].lower())
        else:
            symptom_set.add(symptom.lower())

print symptom_set
print len(symptom_set)

cw = csv.writer(open("symptoms.csv",'w'))
for symptom in symptom_set:
    cw.writerow([symptom])

