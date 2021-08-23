from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

def fetch_data(session,apiKey,country):
    #https://uberall.com/api/storefinders/04AxJXeSBFk4qtBbhQ9JCK1987mtnF/locations/all?v=20171219&language=de&fieldMask=id&fieldMask=identifier&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&
    pass

def getAPIKey(session,country,url):
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = b4(session.get(url,headers=headers).text,'lxml')
    return soup.find('div',{'id':'store-finder-widget','data-key':True,'data-showheader':True,'data-language':True})['data-key']

def getLocsPage(session,country):
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = session.get(country["page"], headers = headers).text
    soup = b4(soup,'lxml')
    locsPage = soup.find('a',{'href':True,'class':True,'target':True,'data-at':lambda x :x and "estaurant" in x,'data-track':lambda x : x and "eader" in x})
    return locsPage
        
def strip_domain(country):
    return '/'.join(country.split('/')[0:3])

def fetch_germany(country):
    domain = strip_domain(country['page'])
    print(domain)
    with SgRequests() as session:
        logzilla.info(f"Attempting to pull {country['text']}")
        locationsPage = getLocsPage(session,country)
        if locationsPage:
            logzilla.info(f"Found locations page {locationsPage}\nLooking for API key")
            apiKey = getAPIKey(session,country,str(domain+locationsPage))
        if locationsPage and apiKey:
            logzilla.info(f"Onto something with {country['text']}\nAPI Key: {apiKey}")
            return fetch_data(session,apiKey,country)
        else if locationsPage:
            isMap = test_for_map(locationsPage)
            if isMap:
                for item in isMap:
                    yield transform_item(isMap,country)
                

if __name__ == "__main__":
    pass
