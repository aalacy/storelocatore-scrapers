# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

address with no numnber,address contains state name,same lat & lng  and i checked all data is true this website

this website redirect to 'https://www.choicehotels.com/en-uk/rodeway-inn?mc=smgogousrwl&cid=Search%7CRodeway%7CUS%7CCore_Brand%7CBMM%7CCPC%7CDesktop%7CEN%7CB_G&ag=US%7CCore%7CGeneral&pmf=GOOGLE&kw=%2Brodeway%20%2Binn&gclid=EAIaIQobChMI3KaVncOU5wIVjJ-zCh2ViA42EAAYASAAEgIVJfD_BwE&gclsrc=aw.ds'