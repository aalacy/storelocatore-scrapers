import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sgselenium import SgSelenium
import time
session = SgRequests()



def write_output(data1,data2):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data1:
            writer.writerow(row)
        for row in data2:
            writer.writerow(row)


def fetch_data1():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.happybank.com"
    while zip_code:
        result_coords = []
        #print("zip_code === " + zip_code)
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        try:
            location_url = "https://www.happybank.com/Locations?bh-sl-address=" + \
                str(zip_code) + "&locpage=search"
            r = session.get(location_url, headers=headers)
        except:
            pass

        soup = BeautifulSoup(r.text, "lxml")
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        script = soup.find_all("script", {"type": "text/javascript"})
        for i in script:
            if "dataRaw" in i.text:
                json_data = json.loads(i.text.split(
                    "JSON.stringify(")[1].split("),")[0])
                current_results_len = len(json_data)
                for data in json_data:
                    location_name = data["name"]
                    street_address = data['address'] + ' ' + data['address2']
                    city = data['city']
                    state = data['state']
                    zipp = data['postal']
                    country_code = data['category']
                    phone = data['phone']
                    # re.sub(r'[\W_]+', '', data['phone'])
                    location_type = data['category']
                    latitude = data['lat']
                    longitude = data['lng']
                    page_url = data['web']
                    # print("https://www.happybank.com/Locations" + page_url)
                    phone = data['phone'].replace("BANK ", "")
                    try:
                        r1 = session.get("https://www.happybank.com/Locations" +
                                          page_url.replace("/Locations", ""), headers=headers)
                    except:
                        continue
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    try:
                        hours_of_operation = " ".join(
                            list(soup1.find("div", {"id": "hours"}).stripped_strings)).split("Special")[0]
                    except:
                        hours_of_operation="<MISSING>"
                    result_coords.append((latitude, longitude))
                    store = [locator_domain, location_name, street_address, city, state, zipp, "US",
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, "https://www.happybank.com/Locations" + page_url]
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    store = [x.encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]

                    # print("data = " + str(store))
                    # print(
                    #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()



def fetch_data2():
    addressesess = []
    r = session.get("https://www.happybank.com/Locations/FindUs/FindanATM")
    soup = BeautifulSoup(r.text, "lxml")
    iframe_link = soup.find(
        "iframe", {"title": "Happy State Bank ATM Locations"})["src"]
    r = session.get(iframe_link)
    soup = BeautifulSoup(r.text, "lxml")
    driver = SgSelenium().chrome()
    addresses = []
    driver.get(iframe_link)
    time.sleep(3)
    driver.find_element_by_xpath(
        "//div[@class='i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c']").click()
    for button in driver.find_elements_by_xpath("//*[contains(text(), '...')]"):
        time.sleep(3)
        button.click()
    for button in driver.find_elements_by_xpath("//div[contains(@index, '')]"):

        try:
            # try:
            #     driver.find_element_by_xpath(
            #         "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
            # except:
            #     pass

            if button.get_attribute("index") == None:
                continue
            time.sleep(3)
            button.click()
            time.sleep(4)

            location_soup = BeautifulSoup(driver.page_source, "lxml")
            # time.sleep(3)
            try:
                driver.find_element_by_xpath(
                    "//div[@class='HzV7m-pbTTYe-KoToPc-ornU0b']").click()
                time.sleep(5)
                # driver.find_element_by_xpath(
                #     "//div[@class='HzV7m-pbTTYe-ibnC6b pbTTYe-ibnC6b-d6wfac']").click()
                # time.sleep(6)
            except:
                pass
            try:
                name = list(location_soup.find(
                    "div", text=re.compile("ATM Name")).parent.stripped_strings)[-1]
            except:
                name = "<MISSING>"
            try:
                street_address = list(location_soup.find(
                    "div", text=re.compile("Street Address")).parent.stripped_strings)[-1]
            except:
                street_address = "<MISSING>"
            try:
                city = list(location_soup.find(
                    "div", text=re.compile("City")).parent.stripped_strings)[-1]
            except:
                city = "<MISSING>"
            try:
                state = list(location_soup.find(
                    "div", text="State").parent.stripped_strings)[-1]
            except:
                state = "<MISSING>"
            try:
                zipp = list(location_soup.find(
                    "div", text=re.compile("Zip Code")).parent.stripped_strings)[-1]
            except:
                zipp = "<MISSING>"

            store = []
            store.append("https://www.happybank.com/")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("ATM")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(
                'https://www.happybank.com/Locations/FindUs/FindanATM')
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressesess:
                continue
            addressesess.append(store[2])
            if store[1] != "<MISSING>":
                # print('data == ' + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
            time.sleep(5)
            driver.find_element_by_xpath(
                "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
        except Exception as e:
            # print(e)
            continue
            time.sleep(3)


def scrape():
    data1 = fetch_data1()
    data2 = fetch_data2()
    write_output(data1, data2)



scrape()
