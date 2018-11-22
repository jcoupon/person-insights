# Person insights

A python search engine to recover public information on a person from a number of sources.

Steps:

- query Forbes and craw to get info (selenium)
- query Wikipedia API (make sure it is a person) flag if not present, record first paragraph if present
- query LinkedIn API
- query news sites (New York Times, bilan.ch) and Twitter: number of articles, most recent
- query search engine result (see https://pypros.com/search-engine-python/)
- see other [APIs](https://github.com/toddmotto/public-apis)

 

TODOs:

- create dictionary to convert country name in 3-letter country code
- modules "Forbes", "Wikipedia APIs", "LinkedIn API"
- if nothing returned, crawl Google
- creates a list of famous/unknown people (100/100?) to build a model
- see for most powerful people from Wikipedia or Forbes
- add a age/year of birth date



## Business understanding

Goals, questions, KPIs## Data acquisition

Data sources, Data environment

### Forbes

Use selenium and [Chrome headless](https://intoli.com/blog/running-selenium-with-headless-chrome/) to crawl the Forbes website.


## Data understanding

Cleansing, Exploration## Modelling

(for famous / politically exposed)## Deployment proposal

System components to make available your insights to our CRM