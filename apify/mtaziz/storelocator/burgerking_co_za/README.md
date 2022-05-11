# The following validation checks ignored

- --ignore CountryCodeFillRateChecker

NOTE: While developing the scrape, it is found that Store URL based on this `tkmaxx.pl` domain is very unstable.
It does not matter whether we're using sgselenium or sgrequests, either way, requests happen to fail resulting 404. 
Retry has been used and got some positive result. Let's say after try 2/3/4/5 times, the requests becomes successful. 
This (`retry`) helps to attain the data for more stores. Total number of stores might be around 50. 
But the crawler might be able to scrape 20 or 30 or 40 or 50. 
It is completely unpredicatable. 
