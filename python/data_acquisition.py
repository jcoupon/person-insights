# import all the necessary libraries
import os
import sys
import selenium
import re
import pandas as pd
import numpy as np
import pickle

import requests
import json

import time
import urllib
import wikipedia
import pycountry
import tweepy

from datetime import date, datetime, timedelta
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

        For PEP, see https://en.wikipedia.org/wiki/Politically_exposed_person
        """

        # To add: youtube, facebook, Instagram
        self.__attributes = [
            'firstname', 'lastname', 'middlename',
            'nationality', 'domicile', 'birth_date',
            'famous', 'famous_comment', 'profession',
            'wealth',  'info', 'linkedin_followers',
            'twitter_followers', 'twitter_verified', 
            'wikipedia_presence', 'Google_search_nresults',
            'Google_news_nresults', 'Financial_news_nresults',
            'nytimes_nresults']

        for a in self.__attributes:
            setattr(self, a, None)

        self.firstname = firstname
        self.lastname = lastname
        self.middlename = middlename
        self.nationality = nationality
        self.domicile = domicile

        # web driver for crawling
        if driver is None:
            self.__driver = launch_browser_driver(headless=True)
        else:
            self.__driver = driver

    def get_info_from_Forbes(self):
        """Method to get info from Forbes. 

        It first goes through the Billionaires list
        then through the powerful people list.
        """

        search_str = ' '.join([self.firstname, self.lastname])

        result = crawl_Forbes(
            self.__driver, search_str, source='billionaires')
        if not result:
            result = crawl_Forbes(
                self.__driver, search_str, source='powerful')

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return


    def get_info_from_Wikipedia(self):
        """Method to get info from Wikipedia """

        result = query_Wikipedia(self.firstname, self.lastname)

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return

    def get_info_from_LinkedIn(self):
        """Method to get info from LinkedIn.
        
        ATTENTION: one need to connect with 
        an existing account first.
        """

        search_str = ' '.join([self.firstname, self.lastname])

        result = crawl_linkedin(
            self.__driver, search_str)

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return

    def get_info_from_Twitter(self):
        """Method to get info from Twitter.
        
        An existing API must be used. 
        See query_Twitter()  
        """

        search_str = ' '.join([self.firstname, self.lastname])

        result = query_Twitter(search_str)

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return

    def get_info_from_Google(self):
        """Method to get info from Google.

        It will query:
        - the Google search
        - The Google news search
        - and a number of financial news 
        website via Google 
        """

        search_str = ' '.join([self.firstname, self.lastname])

        # add quotes to restrict search to 
        # exact name
        search_str = '\"'+search_str+'\"'

        result = crawl_Google_search(
            self.__driver, search_str)

        # fill in attribute wherever 
        # something was found
        for a in self.__attributes:
            try:
                setattr(self, a, result[a])
            except:
                continue    

        return

    def get_info_from_nytimes(self):
        """Method to get info from 
        the New York Times.
        
        An existing API must be used. 
        See query_nytimes
        """

        search_str = ' '.join([self.firstname, self.lastname])

        result = query_nytimes(search_str)

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
        sys.stdout.write('Billionaires list')
        base_url = 'https://www.forbes.com/billionaires/list/#version:realtime_search:'
    if source == 'powerful':
        sys.stdout.write('Most powerful people list')
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
The person might not exist in the {} ranking. \
Or if you suspect this is a crawling issue, rerun with \'headless\'=False to debug.\n'.format(source))

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


def query_Wikipedia(firstname, lastname):
    """Query Wikipedia through its API."""

    search_str = ' '.join([firstname, lastname])

    wikipedia.set_lang("en")

    try:
        person_page = wikipedia.page(search_str)
    except:
        return {}

    soup = BeautifulSoup(person_page.html(), "html.parser")
    
    results = {}
    results['wikipedia_presence'] = 1
    try:
        # results[''] = re.findall(r'{}\s(\w+)*\s{}'.format(firstname, firstname), soup.text)[0].split(' ')[1]
        middle = re.findall(r'(?:{0}\s+)((\S+\s+){{1,2}})(?:{1})'.format(firstname, lastname), soup.text)[0][0]
        if 'and' not in middle.split(' '):
            results['middlename'] = middle
    
    except:
        pass
    try:
        results['birth_date'] = soup.find('span',  {'class': 'bday'}).text
    except:
        pass

    try:
        results['profession'] = soup.find('td',  {'class': 'role'}).text
    except:
        pass

    try:
        results['info'] = wikipedia.summary(search_str)
    except:
        pass

    # TODO look for nationality and domicile
    # results['nationality']
    # results['domicile']

    return results


def crawl_linkedin(driver, search_str):
    """Crawl LinkedIn.com """

    base_url='https://www.linkedin.com/search/results/all/?keywords='
    driver.get(base_url+urllib.parse.quote(search_str))

    # click on green button
    success = persistent_find(
        driver, "//a[@class='search-result__result-link search-result__result-link--visited ember-view']",
        click=True)

    results = {}
    try:
        followers = persistent_find(
            driver, "//span[@class='align-self-center pv-recent-activity-section__follower-count pv-recent-activity-section__follower-count--text pr2 mr2']")
        results['linkedin_followers'] = int(''.join(re.findall(r'\d+', followers)))
    except:
        pass

    try:
        # get the last string as country, 
        # chop off blank space at the beginning 
        country_name = persistent_find(driver, '//h3').split(',')[-1][1:]
        results['domicile'] = pycountry.countries.get(name = country_name).alpha_3
    except:
        pass

    profession = None
    try:

        profession = persistent_find(driver, '//h2')
        #profession = driver.find_element_by_tag_name('h2').text
        results['profession'] = profession
    except:
        pass

    try:
        #experiences = persistent_find(driver,
        #    "//ul[@class='pv-profile-section__section-info section-info pv-profile-section__section-info--has-more']//h3", 
        #    text=False)
        
        # TODO: when several experiences in the 
        # same company
        
        experiences = persistent_find(
            driver, 
            "//div[@id='oc-background-section']//h3", 
            text=False)

        roles = []
        for experience in experiences:
            roles.append(experience.text)
        results['profession'] = ','.join(roles[:3])

    except:
        pass

    return results

def query_Twitter(search_str):
    """Query Twitter API through 
    tweepy to get numner of followers.
    
    The path to Twitter API credentials
    must be given """

    # load credientials
    with open(os.path.join(os.environ['HOME'], 'credentials', 'twitter.json')) as file_in:
        credentials = json.load(file_in)

    # get Twitter API  token
    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['access_token'],credentials['access_token_secret'])
    api = tweepy.API(auth)

    # search users
    users = api.search_users(search_str)

    # fill in results
    # take first result
    results = {}
    try:
        results['twitter_followers'] = users[0].followers_count
    except:
        pass

    try:
        results['twitter_verified'] = users[0].verified
    except:
        pass


    return results


def crawl_Google_search(driver, search_str):
    """Send Google search query and get the number of 
    results for :
    - all search
    - news search
    - and selected financial news site results 
    
    
    https://moz.com/blog/the-ultimate-guide-to-the-google-search-parameters

    """

    results = {}


    # all
    base_url = 'http://www.google.com/search?hl=en&q='
    try:
        driver.get(base_url+urllib.parse.quote(search_str))
        results['Google_search_nresults'] = get_Google_nresults(driver)
    except:
        pass

    # news
    base_url = 'http://www.google.com/search?&tbm=nws&hl=en&q='
    try:
        driver.get(base_url+urllib.parse.quote(search_str))
        results['Google_news_nresults'] = get_Google_nresults(driver)
    except:
        pass

    sites = ['bilan.ch', 'challenges.fr', 'forbes.com', 'ft.com', 'economist.com']
    search_str_financial = search_str + ' ' +' OR '.join(['site:'+s for s in sites])
    try:
        driver.get(base_url+urllib.parse.quote(search_str_financial))
        results['Financial_news_nresults'] = get_Google_nresults(driver)
    except:
        pass
    
    return results


def get_Google_nresults(driver):
    """Return the number of results for a given 
    Google search"""

    # return None if process throws an error
    try:
        # results are stored in the resultStats object
        resultStats = persistent_find(driver, "//div[@id='resultStats']")

        # remove the last two number that correspond 
        # to the query speed
        n = int(''.join(''.join(re.findall(r'\d+', resultStats)[:-2])))
    except:
        n = None

    return n

def query_nytimes(search_str):
    """Query new york Times API through 
    requests to see news visibility.

    Returns number of articles found
    within one year year:0 to 10.
    If 10 it means at least 10.

    The path to New York Times API credentials
    must be given """

    # load credientials
    with open(os.path.join(os.environ['HOME'], 'credentials', 'nytimes.json')) as file_in:
        credentials = json.load(file_in)

    # fill in results
    results = {}
    try:

        # build url for searching articles
        base_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

        # add API key
        url = base_url+'?api-key='+credentials['api-key']

        # add begining date a year ago
        url += '&begin_date={}'.format((datetime.now() - timedelta(days=365)).strftime('%Y%m%d'))

        # add query string
        url += '&q='+urllib.parse.quote(search_str)

        # send query
        response = requests.get(url)

        results['nytimes_nresults'] = len(response.json()['response']['docs'])
    except:
        pass

    return results



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