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
- create a person class (and store data origin)



## Business understanding

Goals, questions, KPIs## Data acquisition

Data sources, Data environment

### Weatlh

- Forbes (use selenium and [Chrome headless](https://intoli.com/blog/running-selenium-with-headless-chrome/) to crawl the Forbes website).
- https://www.wealthx.com/approach/wealth-x-dossier/
- build a correlation Company wealth/CEO wealth (get CEO info from LinkedIn)
- youTube/Facebook/Instagram stars
- Swiss public employees
- Glassdoor salary from LinkedIn profession
- Panama papers
- Politicians: public tax declararion in France, Switzerland, US
- actors/IMBD artist's fee

### Public exposure


wikipedia_presence
Google_search_nresults
Google_news_nresults
Financial_news_nresults

- Wikipedia: Use Wikipedia API with Python package.
- Twitter: number of followers
- startpage: number of results
- Financial news: site:bilan.ch OR site:challenges.fr OR site:forbes.com OR site:ft.com OR site:economist.com
- news website (BBC, New York Times)
- blogs

### Other info

- LinkedIn (via Google?), profession, experience, number of followers
- Google, Wikipedia
- white pages API

## Data understanding

Cleansing, Exploration## Modelling

- create a mock sample

(for famous / politically exposed)## Deployment proposal

System components to make available your insights to our CRM