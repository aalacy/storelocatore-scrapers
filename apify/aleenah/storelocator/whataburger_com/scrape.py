import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sglogging import sglog

driver = SgSelenium().chrome()
log = sglog.SgLogSetup().get_logger(logger_name='whataburger.com')

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


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    urls = []
    driver.get("https://locations.whataburger.com/directory.html")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    statel = re.findall(r'"url":"([^"]*)"', str(soup), re.DOTALL)

    for sl in statel:
        driver.get("https://locations.whataburger.com/" + sl)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tex = re.findall(r'"text/data">{"locs":(.*)}]}</script>', str(soup), re.DOTALL)[0]

        urls += re.findall(r'"url":"([^"]*)"', tex, re.DOTALL)
    num=len(urls)
    log.info(f"Number of locations: {num}")
    for url in urls:
        k = 0
        h = 0
        if "\\u0026" in url:
            url = url.replace("\\u0026", "&")
        if "locations.whataburger.com" not in url:
            url = "https://locations.whataburger.com/" + url
        log.info(url)

        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.c-bread-crumbs-name')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        div = soup.find('div', {'class': 'NAP-main'})
        l = soup.find_all('span', {'class': 'c-bread-crumbs-name'})[3].text
        st = div.find('span', {'class': 'c-address-street-1'}).text
        c = div.find('span', {'class': 'c-address-city'}).text
        s = div.find('abbr', {'class': 'c-address-state'}).text
        z = div.find('span', {'class': 'c-address-postal-code'}).text
        p = div.find('span', {'id': 'telephone'}).text


        id = re.findall(r'.*"id":([0-9\-\(\) ]+)', str(soup))[0]
        la = re.findall(r'.*"latitude":(-?[\d\.]*)', str(soup))[0]
        lo = re.findall(r'.*"longitude":(-?[\d\.]*)', str(soup))[0]
        tim1 = ""
        tim2 = ""
        try:
            tim1 = div.find('div', {'class': 'HoursToday-dineIn'}).text.split('Open Now')[0]
            if 'closed today' in tim1.lower():
                tim1='CLOSED'
            elif 'open 24 hours' in tim1.lower():
                tim1='Open 24 hours'
            elif 'PM'in tim1.lower():
                tim1=tim1.split('PM')[0]+'PM'
        except:
            k = 1

        try:
            tim2 = div.find('div', {'class': 'HoursToday-driveThru'}).text.replace("\n", ",").split('Open Now')[0]
            if 'closed today' in tim2.lower():
                tim2='CLOSED'
            elif 'open 24 hours' in tim2.lower():
                tim2='Open 24 hours'
            elif 'PM'in tim2.lower():
                tim2=tim2.split('PM')[0]+'PM'
        except:
            h = 1

        if k == 1 and h == 1:
            types.append("driveThru")
            locs.append(l)
            street.append(st)
            cities.append(c)
            states.append(s)
            zips.append(z)
            phones.append(p)
            timing.append("<MISSING>")
            lat.append(la)
            long.append(lo)
            ids.append(id)
            page_url.append(url)
        else:
            if tim1 == tim2 and tim1 != "":
                types.append("dineIn, driveThru")
                locs.append(l)
                street.append(st)
                cities.append(c)
                states.append(s)
                zips.append(z)
                phones.append(p)
                timing.append("MON-SUN: " + tim1.strip())
                lat.append(la)
                long.append(lo)
                ids.append(id)
                page_url.append(url)

            elif tim1 == "":
                types.append("driveThru")
                locs.append(l)
                street.append(st)
                cities.append(c)
                states.append(s)
                zips.append(z)
                phones.append(p)
                timing.append("MON-SUN: " + tim2.strip())
                lat.append(la)
                long.append(lo)
                ids.append(id)
                page_url.append(url)

            elif tim2 == "":
                types.append("dineIn")
                locs.append(l)
                street.append(st)
                cities.append(c)
                states.append(s)
                zips.append(z)
                phones.append(p)
                timing.append("MON-SUN: " + tim1.strip())
                lat.append(la)
                long.append(lo)
                ids.append(id)
                page_url.append(url)

            else:
                types.append("dineIn, driveThru")
                locs.append(l)
                street.append(st)
                cities.append(c)
                states.append(s)
                zips.append(z)
                phones.append(p)
                timing.append("MON-SUN: " + tim1.strip() +" Drive Thru: MON-SUN: " + tim2.strip() )
                lat.append(la)
                long.append(lo)
                ids.append(id)
                page_url.append(url)


    all = []
    for i in range(0, len(locs)):
        row = []

        row.append("https://whataburger.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
