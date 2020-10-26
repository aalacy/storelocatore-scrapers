import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape

from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait


session = SgRequests()




# import sgzip


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


countries = {}


def getcountrygeo():
    data = session.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    point = Point(float(lon), float(lat))
    for country, geom in countries.items():
        if geom.contains(point):
            return country

    return "unknown"


def fetch_data():
    driver = SgSelenium().firefox()
    getcountrygeo()
    # zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    locator_domain = "https://www.petermillar.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # r1 = session.get('https://www.petermillar.com/f/about-us/our-stores.html', headers=headers)
    # soup1 = BeautifulSoup(r1.text, "lxml")
    # driver.get("https://www.petermillar.com/f/about-us/our-stores.html")
    # soup = BeautifulSoup(driver.page_source, "lxml")

    driver.get("https://www.petermillar.com/f/about-us/our-stores.html")
    s = requests.Session()
    cookies_list = driver.get_cookies()

    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")

    # print(cookies_string)

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Cookie": cookies_string


    }
    add = []
    hours = []
    page_url1 = []
    data = s.get(
        "https://www.petermillar.com/f/about-us/our-stores.html", headers=headers)
    soup = BeautifulSoup(data.text, "lxml")
    data = soup.find_all("a", {"class": "primary"})
    for link in data:
        # data1 = BeautifulSoup(link,'lxml')
        if "/f/store-locator" in link['href']:
            if "https://www.petermillar.com/f/store-locator/dallas-tx-peter-millar-mens-clothing-store.html" in link['href']:
                data2 = s.get(link['href'], headers=headers)
                page_url1.append(link['href'])
                # print("https://www.petermillar.com"+link['href'])
                # soup2 = BeautifulSoup(driver.page_source, "lxml")
                soup3 = BeautifulSoup(data2.text, "lxml")
                # print(soup3.find_all("div",{"class":"col col-text"})[1])
                add.append(soup3.find_all("div", {"class": "col col-text"})[
                           1].text.strip().replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("-", "").strip())
                hours.append(soup3.find_all(
                    "div", {"class": "col col-text"})[-1].text.strip())
            else:
                data2 = s.get("https://www.petermillar.com" +
                              link['href'], headers=headers)
                page_url1.append("https://www.petermillar.com" + link['href'])
                # print("https://www.petermillar.com"+link['href'])
                # soup2 = BeautifulSoup(driver.page_source, "lxml")
                soup2 = BeautifulSoup(data2.text, "lxml")
                add.append(soup2.find_all("div", {"class": "col col-text"})[
                           1].text.strip().replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("-", "").strip())
                hours.append(soup2.find_all(
                    "div", {"class": "col col-text"})[-1].text.strip())

    # print("----------------hours-----",hours)
    # print("---------------add------",add)
    # exit()
    r = session.get(
        'https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/2295/stores.js?callback=SMcallback2', headers=headers)
    # .text.strip().replace("(","").replace(")","").replace(" ","-")
    script = "".join(r.text.split('SMcallback2(')[1].split(')'))
    json_data = json.loads(script)
    for x in json_data['stores']:
        # if x['url']:
            # print(x['url'])
        latitude = x['latitude']
        longitude = x['longitude']
        country_name = getplace(latitude, longitude)
        # print("country_name === "+str(country_name))
        if "United States of America" != country_name and "Canada" != country_name:
            continue
        else:
            hours_of_operation = ''
            page_url2 = ''
            for q in range(len(hours)):
                if x['phone'] != None:
                    # print(x['phone'].replace("(","").replace(")","").replace(" ","-"))
                    # print("------------------======================")
                    if x['phone'].strip().replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("-", "").strip() == add[q].strip():
                        # print(x['phone'].strip().replace("(", "").replace(")", "").replace(
                        #     " ", "").replace(".", "").replace("-", "").strip() + " " + add[q].strip())
                        # print(page_url1[q])
                        # print("~~~~~~~~~~~~~~~")
                        hours_of_operation = hours[q].replace(
                            "Store Manager: Lachan Medley", "Mon - Fri: 9 am - 6 pm, Sat: 9 am - 5 pm, Sun: 1 pm - 5 pm Christmas Eve: 9 am - 3 pm Christmas Day: Closed December 26th: Closed  New Year's Eve: 9 am - 3 pm New Year's Day: Closed")
                        page_url2 = page_url1[q]
            # print(x['address'].strip())
            store_number = x['id']
            location_name = x['name'].replace(
                '&AMP;', 'and').replace('(', '').capitalize()
            zipp_list = " ".join(x['address'].split(',')[1:])
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_list))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_list))
            if us_zip_list:
                zipp = us_zip_list[0]
                country_code = "US"
            elif ca_zip_list:
                zipp = ca_zip_list[0]
                country_code = "CA"
            else:
                # print("country_name === "+str(country_name))
                if "United States of America" == country_name:
                    zipp = "<MISSING>"
                    country_code = "US"
                else:
                    zipp = "<MISSING>"
                    country_code = "CA"

            # print(zipp,country_code)
            # print('~~~~~~~~~~~~~~~~~~~~~')

            address = x['address'].split(',')
            if " United States" in address:
                address.remove(' United States')
            if len(address) == 7:
                street_address = address[2] + " " + address[3]
                city = address[3]
                state = address[-2]
            elif len(address) == 6:
                street_address = address[1] + " " + address[2]
                city = address[3]
                state = address[-2]

                # print(state)

            elif len(address) == 5:
                if " Vero Beach" not in address:
                    street_address = address[0].replace('&amp;Amp;', 'and').replace(
                        '/', ' ') + " " + address[1].replace('&amp;Amp;', 'and')
                    # street_address = staddress.split('  ')[0:].replace('&amp;Amp;','')
                    city = address[2].replace(' Suite X21', '')
                    state = address[3]
                else:
                    street_address = " ".join(address[:3])
                    city = address[3]
                    state = address[-1].split()[0]

            elif len(address) == 4:
                if 'Inwood Village' not in address and 'Town Square' not in address:
                    street_address = address[0].replace(
                        'Inwood Village', '').replace('Town Square', '').strip()
                    city = address[1]
                    # print(address[-2])
                    state_list = re.findall(
                        r' ([A-Z]{2}) ', str(" ".join(address[1:]).strip()))
                    if state_list == []:
                        state = address[-1].strip()
                        # print(address)

                    else:
                        state = "".join(state_list).strip()
                    # print(state)
                else:
                    street_address = " ".join(address[:2])
                    city = address[2]
                    state = address[-1].split()[0]

            elif len(address) == 3:
                if "Carmel Plaza" not in address:
                    street_address = address[0]
                    city = address[1].replace('Suite G108', '').replace(
                        'Suite 20', '').replace('#950', '')
                    state = address[-1].split()[0]

                else:
                    street_address = address[0] + " " + address[1]
                    city = address[-2].split()[-1]
                    state = address[-1].split()[0]

            elif len(address) == 2:
                # print(address)
                # print(len(address))
                street_address = address[0].replace('\n', ' ').replace('Greenville', '').replace('Huntsville', '').replace(
                    'Chestnut Hill', '').replace('Palm Desert', '').replace('S Tifton', '').replace('Atlantic City', '').strip()
                city = " ".join(address[0].split()[-2:]
                                ).replace('1603', '').replace('8', '')
                state = address[-1].split()[0]
            else:
                st_address = address[0].split('.')
                if len(st_address) == 3:
                    street_address = " ".join(st_address[:-1]).strip()
                    city = st_address[-1].split()[0]
                    state = st_address[-1].split()[1]
                    zipp = st_address[-1].split()[-1]
                    # print(street_address +" | "+city+ " | "+state+" | "+zipp+ " | "+country_code)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                else:
                    street_address = " ".join(st_address)
                    if "Scottsdale" in street_address:
                        city = "Scottsdale"
                    else:
                        city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                # print(street_address +" | "+city+ " | "+state+" | "+zipp+ " | "+country_code)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            street_address = street_address.replace(
                '>', '').capitalize().strip()

            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(x['phone']))
            if phone_list != []:
                phone = phone_list[0].strip()
            else:
                phone = "<MISSING>"

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url2]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        if street_address in addresses:
            continue
        addresses.append(street_address)
        # print(state)
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
