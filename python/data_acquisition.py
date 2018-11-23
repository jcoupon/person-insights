# import all the necessary libraries
import os
import sys
import selenium
import re
import pandas as pd
import numpy as np
import pickle

import time
import urllib
import pycountry
from datetime import date
from bs4 import BeautifulSoup

"""


Class for a person


"""

class Person(object):

    def __init__(
            self, firstname, lastname, 
            middlename = None, nationality = None, domicile = None, 
            driver = None):
        """Initialization

        TODO: add corresponding source of info
        """

        self.__attributes = [
            'firstname', 'lastname', 'middlename',
            'nationality', 'domicile', 'birth_date',
            'famous', 'famous_comment', 'profession',
            'wealth',  'info']

        self.firstname = firstname
        self.lastname = lastname
        self.middlename = middlename
        self.nationality = nationality
        self.domicile = domicile
        self.birth_date = None
        self.famous = None
        self.famous_comment = None
        self.profession = None
        self.wealth = None
        self.info = None

        # web driver for crawling
        if driver is None:
            self.__driver = launch_browser_driver(headless=True)
        else:
            self.__driver = driver

    def get_info_from_Forbes(self):

        search_str = ' '.join([self.firstname, self.lastname])
        result = crawl_Forbes(
            self.__driver, search_str)

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return


    def print_info(self):
        """Print the person's info
        """

        # loop over attributes
        # exclude private and 
        # callable ones

        '''
        attributes = [
            a for a in dir(self) 
            if not a.startswith('__') 
            and not a.startswith('_') 
            and not callable(getattr(self,a))
            ]
        '''

        for a in self.__attributes:
            print(a, ':', getattr(self, a))

        pass


def launch_browser_driver(headless=True):
    """Function that launches an Chrome browser 
    instance to crawl the web """

    # Import Selenium and configure 
    # Chrome headless options
    import selenium.webdriver as webdriver

    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument('headless')

    # set the window size
    options.add_argument('window-size=1200x600')
    options.add_argument("--mute-audio")

    # initialize the driver
    driver = webdriver.Chrome(options=options)

    return driver


def crawl_Forbes(driver, search_str, source='billionaires'):
    """Crawl Frobes web site to get 
    information.
    
    The step requiring the acceptance 
    of the cookies is a little unstable 
    so we need to wait a few seconds before 
    and after.

    skip_get is only for debugging
    
    """

    sys.stdout.write('Crawling Forbes.com: start.\n')

    base_url = None
    if source == 'billionaires':
        base_url = 'https://www.forbes.com/billionaires/list/#version:realtime_search:'
    if source == 'powerful':
        base_url = 'https://www.forbes.com/powerful-people/list/#tab:overall_search:'
    
    driver.get(base_url+urllib.parse.quote(search_str))

    # print(driver.get_cookies())

    # if Cookies consent found, 
    # find and click on green button
    if driver.find_elements_by_xpath("/html/body/div[@id='teconsent']"):

        sys.stdout.write('Cookies consent window found, clicking on green button.\n')

        # switch to consent frame
        time.sleep(5)
        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

        # click on green button
        success = persistent_find(driver, "//a[@class='call']", click=True)

        if not success:
            sys.stdout.write('The cookies consent step failed. \
Forbes.com website was not crawled. Please rerun\n')

            return None

        # wait again a bit and reload wanted url
        time.sleep(3)
        driver.get(base_url+urllib.parse.quote(search_str))

    # refresh required for the query to be sent
    driver.refresh()

    success = persistent_find(
        driver, 
        "//tbody[@id='list-table-body']//a[@class='exit_trigger_set']", 
        click=True, verbose=True)

    if not success:
        sys.stdout.write('The Forbes.com crawling failed. \
The person might not exist in the Billionaires ranking. \
Or if you suspect this is a crawling issue, rerun with \'headless\'=False to debug.\n')

        return None

    sys.stdout.write('Crawling Forbes.com: the person was found. Extracting info...\n')

    # get stat values
    stats_values = {}
    stats = persistent_find(driver, "//div[@class='profile-stats__item']", text=False)
    for stat in stats:
        key = stat.find_element_by_class_name('profile-stats__title').text
        value = stat.find_element_by_class_name('profile-stats__text').text
        stats_values[key] = value
    stats_values

    # fill in result dictionary
    result = {}
    try:
        country_name = stats_values['CITIZENSHIP']
        result['nationality'] = pycountry.countries.get(name = country_name).alpha_3
    except:
        pass
        
    try:
        country_name = stats_values['RESIDENCE'].split(',')[1][1:]
        try:
            result['domicile'] = pycountry.countries.get(name = country_name).alpha_3
        except:
            # if not found in counrty list
            # it's a US state
            result['domicile'] = 'USA'
    except:
        pass

    try:
        result['birth_date'] = date.today().year - int(stats_values['AGE'])
    except:
        pass

    try:
        result['profession'] = stats_values['SOURCE OF WEALTH']
    except:
        pass

    # wealth in million USD
    try:
        wealth_str = driver.find_element_by_xpath("//div[@class='profile-info__item__value']").text
        result['wealth'] = float(re.findall(r'\d+\.\d+', wealth_str)[0])*1000
    except:
        pass
    result['info'] = driver.find_element_by_xpath("//div[@class='profile-text']").text

    sys.stdout.write('Crawling Forbes.com: end\n')
  
    return result


def persistent_find(driver, xpath_element, click=False, text=True, verbose=False, n_retries=5):
    """ Find the element content by retrying a couple of time"""

    for retry in range(n_retries):
        try:
            # wait a few secs to properly load the results
            time.sleep(3)

            # try to find the elements
            elements = driver.find_elements_by_xpath(xpath_element)

            # click to link
            if click:
                elements[0].click()
                return 'click successful'
            
            # exit loop if click process did not
            # return any error
            if text:
                return elements[0].text
            else:
                return elements

        except:
            if verbose:
                sys.stdout.write(
                    'Crawling: retrying...{}/{}\n'.format(retry+1, n_retries))
            continue

    return None