import csv
import re
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from sgselenium import SgSelenium

driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    US_states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
                 "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
                 "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
                 "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
                 "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                 "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
                 "West Virginia", "Wisconsin", "Wyoming"]

    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    driver.get("https://rockyrococo.com/locations")

    time.sleep(15)
    driver.switch_to.frame(driver.find_element_by_id("bullseye_iframe"))

    #print("here")
    for us in US_states:
        print(us)
        driver.find_element_by_id('txtCityStateZip').clear()
        driver.find_element_by_id('txtCityStateZip').send_keys(us)
        driver.find_element_by_id("ContentPlaceHolder1_searchButton").click()
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        divs = soup.find_all('address')
        for div in divs:
            add=div.text.strip().split("\n")
            street.append(add[0])
            addr=add[2].split(",")
            cities.append(addr[0])
            addr=addr[1].strip().split(" ")
            states.append(addr[0])
            zips.append(addr[1])
            phones.append(add[4].strip())
        h3s= soup.find_all('h3',{'itemprop':'name'})
        for h3 in h3s:
            locs.append(h3.text)
        uls=soup.find_all('div',{'class':'resultsDetails'})
        for ul in uls:
            metas=ul.find_all("meta")
            lat.append(metas[0].get("content"))
            long.append(metas[1].get("content"))
            page_url.append(ul.find('ul',{'class':'resultsDetailLinks'}).find('a').get('href'))

    #print(len(page_url))
    #print(page_url)
    #print("here")

    for url in page_url:  #for timing
        if url.startswith('//'):
            url = 'http:' + url
        # print(url)
        driver.get(url)
        try:
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]')))
        except:
            timing.append("<MISSING>")
            #print("passed")
            continue
        #tex=driver.find_element_by_xpath('/html/body/div[6]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]').text
        time.sleep(1)
        tex=element.text


        tim = re.findall(r'Hours:(.*pm)',tex,re.DOTALL)[0].strip().replace("\n"," ")
        timing.append(tim)


    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://rockyrococo.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append("https://rockyrococo.com/locations")  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
