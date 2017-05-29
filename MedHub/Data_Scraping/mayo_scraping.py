import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import string
from collections import defaultdict
import pickle
import csv

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_extension('uBlock-Origin_v1.12.0.crx')
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options = chromeOptions)

def try_finding_tag_name(location, tag_name, disease_name):
    if not location:
        return None
    try:
        return location.find_elements_by_tag_name(tag_name)
    except (NoSuchElementException, StaleElementReferenceException) as e:
        return None

def scrape_text(text_iterator):
    if text_iterator:
        text_list = []
        try:
            for text_el in text_iterator:
                text_list.append(text_el.text.strip())
            return ' '.join(text_list)
        except (NoSuchElementException, StaleElementReferenceException) as e:
            return ''
    else:
        return ''

def dd():
    return defaultdict(str)

disease_dict = defaultdict(dd)
text_title = ['Symptom', 'Treatment']
n_title = len(text_title)
links_visited = set()
failed_diseases = set()


for letter in string.ascii_uppercase:
    driver.get('https://www.mayoclinic.org/diseases-conditions/index?letter=%s' % letter)
    num_links = len(driver.find_elements_by_xpath('//*[@id="index"]/ol/li'))
    for i in range(1, num_links + 1):
        disease_link = driver.find_element_by_xpath('//*[@id="index"]/ol/li[%d]/a' % i)
        disease_json = "{%s}"
        disease_name = disease_link.text.lower()
        link = disease_link.get_attribute('href')
        if link not in links_visited:
            print "Starting %s" % disease_name
            links_visited.add(link)
            disease_dict[disease_name]["link"] = disease_link.get_attribute('href')
            disease_link.click()
        else:
            continue

        try:
            text_location = driver.find_element_by_xpath('//*[@id="mayoform"]/div[4]/article/div[2]/div[1]/div[2]')
            disease_dict[disease_name]["overview"] = {}
        except (NoSuchElementException, StaleElementReferenceException) as e:
            try:
                text_location = driver.find_element_by_xpath('//*[@id="main-content"]')
            except (NoSuchElementException, StaleElementReferenceException) as e:
                text_location = None

        text_p_tag = try_finding_tag_name(text_location, 'p', disease_name)
        text_li_tag = try_finding_tag_name(text_location, 'li', disease_name)

        disease_dict[disease_name]["overview"] = {"paragraph_text": scrape_text(text_p_tag), \
                                                  "list_text": scrape_text(text_li_tag)}


        for i in range(n_title):
            try:
                driver.find_element_by_partial_link_text(text_title[i]).click()
            except (NoSuchElementException, StaleElementReferenceException) as e:
                if i == n_title - 1:
                    failed_diseases.add(disease_name)
                    break
                else:
                    continue

            try:
                text_location = driver.find_element_by_xpath('//*[@id="mayoform"]/div[4]/article/div[2]/div[1]/div[2]')
            except (NoSuchElementException, StaleElementReferenceException) as e:
                try:
                    text_location = driver.find_element_by_xpath('//*[@id="main-content"]')
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    failed_diseases = failed_diseases.add(disease_name)
                    break

            text_p_tag = try_finding_tag_name(text_location, 'p', disease_name)
            text_li_tag = try_finding_tag_name(text_location, 'li', disease_name)

            disease_dict[disease_name][text_title[i].lower()] = {"paragraph_text" : scrape_text(text_p_tag), \
                                                                 "list_text" : scrape_text(text_li_tag)}

        driver.get('https://www.mayoclinic.org/diseases-conditions/index?letter=%s' % letter)

    pickle.dump(disease_dict, open("disease_dictionaries/disease_dict_A_to_%s.p" % letter, "wb"))

    cw = csv.writer(open("failed_diseases/failed_diseases_A_to_%s.csv" % letter,'w'))
    for disease in failed_diseases:
        cw.writerow([disease])

raw_input("Press Enter to quit")
driver.quit() # close browser