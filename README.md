# Person insights

This module is a python search engine to recover public information on a person from a number of sources.

Steps:

- query Forbes and craw to get info (selenium)
- query Wikipedia API, flag if present, scrape info and get summary if present
- query LinkedIn API, get profession and past experiences
- query Twitter, number of followers, whether it's a verified account
- crawl Google search, news and a number of news sites (Financial times, The economist, bilan.ch, challenges.fr)
- query New York Times API
- build a model to predict if person is famous/politically exposed mainly from online presence
- apply model and record probability

Further improvements:
- see other [APIs](https://github.com/toddmotto/public-apis)
- create dictionary to convert country name in 3-letter country code
- create a model to estimate wealth
- create an option to return wealth in different units


## How to use it

See `notebook/search engine.ipynb` for more details. The current workflow is the following:

- Launch web driver with window to control behavior:
```python
driver = data_acquisition.launch_browser_driver(headless=False)
```
- create person object (info will contain only firstname and lastname):
```python
person = data_acquisition.Person('Jeff', 'Bezos', middlename='Preston', driver=driver)
```
```python
person.print_info()
```
- get info sequentially
```python
person.get_info_from_Forbes()
person.get_info_from_Wikipedia()
person.get_info_from_LinkedIn()
person.get_info_from_Twitter()
person.get_info_from_Google()
person.get_info_from_nytimes()
```
- print results
```python
person.print_info()
```
- run famous people model
```python
reload(data_modeling)
data_modeling.predict_PEP(person)
```
- print final information
```python
person.print_info()
```


## Data sources
### Weatlh

Below is a list of additional sources of information:

- Forbes (use selenium and [Chrome headless](https://intoli.com/blog/running-selenium-with-headless-chrome/) to crawl the Forbes website).
- another [source](https://www.wealthx.com/approach/wealth-x-dossier/) of wealth information
- build a correlation Company wealth/CEO wealth (get CEO info from LinkedIn)
- youTube/Facebook/Instagram stars
- Swiss public employees
- Glassdoor salary from LinkedIn profession
- Panama papers
- Politicians: public tax declararion in France, Switzerland, US
- actors/IMBD artist's fee

### Public exposure

Features:

- `wikipedia_presence`
- `Google_search_nresults`
- `Google_news_nresults`
- `Financial_news_nresults`
- `nytimes_nresults`

Sources:

- Wikipedia: Use Wikipedia API with Python package.
- Twitter: number of followers
- startpage: number of results
- Financial news: site:bilan.ch OR site:challenges.fr OR site:forbes.com OR site:ft.com OR site:economist.com
- news website (BBC, New York Times)
- blogs
- CIA [worldfactbook](https://www.cia.gov/library/publications/download/)

### Other info

- LinkedIn (via Google?), profession, experience, number of followers
- Google, Wikipedia
- white pages API
