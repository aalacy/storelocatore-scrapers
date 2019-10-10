import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from bs4 import BeautifulSoup
import requests
import time


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

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

    driver.get("https://studiobarre.com/find-your-studio/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    statel=soup.find_all('div',{'style':'padding-top:50px; padding-bottom:0px; background-color:'})

    for sl in statel:
        h5s = sl.find_all("h5")
        for h in h5s:
            a= h.find("a")
            locs.append(a.text)
            page_url.append(a.get('href'))

    for url in page_url:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        l=soup.find('h2',{'class':'elementor-heading-title elementor-size-default'}).text.split(",")[0]
        print(l)
        spans = soup.find_all('span', {'class': 'elementor-icon-list-text'})
        addr=spans[0].text

        phones.append(re.sub(r'[\{\}a-z ]*',"",spans[1].text.strip()))
        z= re.findall(r'[0-9]{5}',addr)[-1]
        try:
            s=re.findall(r'[A-Z]{2}',addr)[-1]
            street.append(addr.replace(l, "").replace(z, "").replace(s, "").replace(",", "").strip())
        except:
            s="<MISSING>"
            street.append(addr.replace(l,"").replace(z,"").replace(",","").strip())


        cities.append(l)
        states.append(s)
        zips.append(z)
        try:
            div = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div/div/section[4]")
        except:
            div = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div/section[4]")

        divas = div.find_elements_by_class_name("elementor-widget-container")
        del divas[0]
        del divas[0]
        tim = ""

        for div in divas:

            try:
                h3s= div.find_element_by_tag_name('h3')
            except:
                break
            dvs = div.find_elements_by_class_name('desc')

            tim += h3s.text
            for ds in dvs:
                tim += " " + ds.text + " "

            if dvs ==[]:
                s = str(soup)
                divs=re.findall(r'<!--div class="desc">(.*)</div-->',s)
                tim +=" "+divs[divas.index(div)]+" "

            tim=tim.replace("\n"," ")
        if tim =="":
            tim="<MISSING>"
        timing.append(tim.strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://studiobarre.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
