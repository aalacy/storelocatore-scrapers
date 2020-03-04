import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    page_url = []

    #headers = {':authority': 'qoe-1.yottaa.net', ':method': ' GET','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}

    sls=[]
    url_list=["https://www.ralphlauren.com/Stores-ShowStates?countryCode=CA","https://www.ralphlauren.com/Stores-ShowStates?countryCode=US"]
    for url in url_list:
        res=session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #print("soup")
        sls += soup.find('div', {'class': 'store-directory-states'}).find_all('a')
    """sls.append("https://www.ralphlauren.com/Stores-ShowCities?countryCode=GB")
    for s in sls:
            res = session.get(s.get('href'))
            soup = BeautifulSoup(res.text, 'html.parser')
            cls = soup.find('div', {'class': 'store-directory-cities'}).find_all('a')

            for c in cls:
                res = session.get(c.get('href'))
                soup = BeautifulSoup(res.text, 'html.parser')
                div = soup.find('div', {'class': 'store-locator-details'})
                l= div.find('h1').text
                print(div.find('p',{'class':'store-address'}).text)"""
fetch_data()