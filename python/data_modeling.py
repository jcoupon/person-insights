# import all the necessary libraries

import os
import sys
from importlib import reload
import numpy as np
import requests
import json
import time
import urllib
import re
import pickle

import wikipedia
import selenium
import pycountry
import tweepy

from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import unidecode
import pandas as pd

import data_acquisition

from sklearn import preprocessing
from sklearn import model_selection
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn import metrics
from sklearn import discriminant_analysis
from sklearn import svm

"""


functions


"""


def get_soup(url):
    """Get page content using 
    Beautiful soup package.
    """
    page = requests.get(url)
    if page.status_code == 200:
        # convert page content into a beautifulsoup object
        soup = BeautifulSoup(page.content, "html.parser")
    else:
        raise Exception('the page cannot be found')
    
    return soup



def clean_name(name):
    """Replace non UTF-8
    characters and remove anything
    but alphanumeric characters
    """
    
    name = unidecode.unidecode(name)
    name = ' '.join(re.findall(r'\w+', name))

    return name


def csv_to_people_list(path):
    """Read csv file and transform it
    into list of person objects"""
    
    people_list = []
    
    try:
        df = pd.read_csv(path)
    except:
        return []
        
    # loop over csv file rows
    for i in range(len(df)):
        
        # create new person
        person = data_acquisition.Person(
            '', '', driver=False)
        
        # fill in it with info
        try:
            for a in data_acquisition.ATTRIBUTES:
                setattr(person, a, df.iloc[i][a])
        except:
            pass
        
        people_list.append(person)
        
    return people_list


def people_list_to_csv(people_list, path):
    """Loop over people list
    and write it as csv file"""
    
    # create a temporary dictionary
    dict_temp = {}
    for a in data_acquisition.ATTRIBUTES:
        dict_temp[a] = []
        
    # loop over list
    for person in people_list:
        for a in data_acquisition.ATTRIBUTES:
            dict_temp[a].append(getattr(person, a))
    
    pd.DataFrame(dict_temp).to_csv(path, index=False)

    # df_temp = pd.read_csv('non_PEP_people_info.csv')    

    return


def add_driver(people_list, driver):
    """Add driver to each person in 
    people_list"""
    
    
    for person in people_list:
        person.set_driver(driver)
    
    return


def classify(X, y, classifier, prob=None, random_seed=20091982):
    """ Run classifier and print
    results
    """
    
    X_train, X_test, y_train, y_test = \
    model_selection.train_test_split(
        X, y, test_size=0.20, random_state=random_seed)
    
    classifier.fit(X_train, y_train)
    if prob is not None:
        y_pred = classifier.predict_proba(X_test)[:,0] < prob
    else:
        y_pred = classifier.predict(X_test)
        
 
    N = len(y_test)
    TP = np.sum((y_pred == y_test) & (y_test == 1))
    TN = np.sum((y_pred == y_test) & (y_test == 0))
    FP = np.sum((y_pred != y_test) & (y_pred == 1))
    FN = np.sum((y_pred != y_test) & (y_pred == 0))

    accuracy = (TP+TN)/N
    precision = TP/(TP+FP)
    recall = TP/(TP+FN)

    result_string = 'N={0}, TP={1}, TN={2}, FP={3}, FN={4}\n'.format(N, TP, TN, FP, FN)
    result_string += \
        'Precision: {0:.4f}, recall: {1:.4f}, accuracy: {2:.4f}'\
        .format(precision, recall, accuracy)

    print(result_string)
    
    report = metrics.classification_report(y_test, y_pred)
    
    
    print(report)
    
    return classifier

def get_feature_importances(cols, importances):
    
    count = 0
    indices = np.argsort(importances)[::-1]
    for i in indices:
        print('{1}: {0:.2f}%'.format(
            importances[i]*100.0, cols[i]))
        count += 1
        #if count == 10:
        #    break
    return


FEATURES = ['log10_Google_search_nresults', 
            'log10_Google_news_nresults',
            'wikipedia_presence', 
            'log10_twitter_followers',
            'log10_Financial_news_nresults',
             'nytimes_nresults']

def build_feature_vector(df, features=FEATURES):

  
    df['log10_Google_search_nresults'] = np.log10(1.0+df['Google_search_nresults'].fillna(0))
    df['log10_Google_news_nresults'] = np.log10(1.0+df['Google_news_nresults'].fillna(0))
    df['log10_twitter_followers'] = np.log10(1.0+df['twitter_followers'].fillna(0))
    df['wikipedia_presence'] = df['wikipedia_presence'].fillna(0)
    df['log10_Financial_news_nresults'] = np.log10(1.0+df['Financial_news_nresults'].fillna(0))
    df['nytimes_nresults'] = df['nytimes_nresults'].fillna(0)
   
    
    return df[features].values


def predict_PEP(person):
    """Predict if person is famous or not """

    # create feature vector
    dict_temp = {}
    for a in data_acquisition.ATTRIBUTES:
        dict_temp[a] = [getattr(person, a)]
    person_df = pd.DataFrame(dict_temp)

    X = build_feature_vector(person_df)

    # load model
    with open('../data/model.pickle', 'rb') as file_in:
            classifier = pickle.load(file_in)

    person.famous = classifier.predict_proba(X)[:,1][0] > 0.5
    person.famous_comment = classifier.predict_proba(X)[:,1][0]

    return