### Introduction

These tools rely on python using the requests module (https://2.python-requests.org/en/master/) and the
beautiful soup module (https://www.crummy.com/software/BeautifulSoup/bs4/doc/).


## Installation
To install the dependencies, make sure to `pip install requests` and `pip install bs4`

## Running
To run, simply open the terminal of your choice and `cd path/to/scripts/here`. Then `python marriot.py` or `python shopnsavefood.py.
Alternatively if you are on a linux system you may need to run `python3 script.py` as opposed to `python script.py`.

## Output
Output will be auto-generated into csv files inside the current working directory. 


# Notes

One thing that is particularly great about python with requests whether or not the team ends up going with me, is that it is quite easy
to modify the scripts built in this fashion to handle proxies if needed for anysites. As well, setting custom headers is only an extra
1 or 2 lines of code depending on how elegant you want everything to look.

As well, compared to running a headless browser it is much more simple to setup for auto running on a server. As well, the run speed will
be roughly an order of magnitude faster than running headless browsers.
(Solutions can be made to speed up headless browser scraping significantly, but most people are unaware of those solutions)
