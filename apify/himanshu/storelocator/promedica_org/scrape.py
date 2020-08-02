import csv
import re
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
import requests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)






def fetch_data():
    driver = SgSelenium().firefox()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    base_url = "https://www.promedica.org"
    addresses = []

    # driver.get('https://www.promedica.org/Pages/OHAM/OrgUnitsSearchResult.aspx?Radius=-1&IncludeChildUnits=1&IncludeLinkedUnits=0&IncludeCurrent=True&RadiusUnit=Miles&PostalCodeControlHidden=False&RadiusControlHidden=False&RadiusUnitDefault=Any%20Distance&RadiusLabelText=Search%20Within&TypeIds=0')
    driver.get('https://www.promedica.org/Pages/OHAM/OrgUnitsSearchResult.aspx')


    isLast = False
    while not isLast:
        soup = BeautifulSoup(driver.page_source,"lxml")
        for loc_detail in soup.find_all("a",{"class":"location-search-results"}):
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
            page_url = ""

            # do your logic here.
            page_url = loc_detail["href"]
            # page_url = 'https://www.promedica.org/Pages/OHAM/OrgUnitDetails.aspx?OrganizationalUnitId=823'
            # page_url = 'https://www.promedica.org/Pages/OHAM/OrgUnitDetails.aspx?OrganizationalUnitId=1120'
            # print("page_url = ",page_url)
            r_location = requests.get(page_url, headers=headers)
            try:
                soup_location = BeautifulSoup(r_location.text, "lxml")
            except:
                pass
            if soup_location.find("h1",{"class":"loc-top-image"}):
                # store_number = loc_detail.find("OrganizationID").next
                full_address = list(soup_location.find("div",{"class":"address-block xs-mbm"}).find("a").stripped_strings)
                # print("full_address == ", full_address)
                if len(full_address) > 1:
                    location_name = soup_location.find("h1",{"class":"loc-top-image"}).text
                    phone = soup_location.find("a",{"class":"phone"}).text
                    street_address = ", ".join(full_address[:-1])
                    if "Suite" in street_address:
                        street_address = "".join(street_address[:street_address.index("Suite")])
                    if "suite" in street_address:
                        street_address = "".join(street_address[:street_address.index("suite")])
                    if "Floor" in street_address:
                        street_address = "".join(street_address[:street_address.index("Floor")])
                    if "floor" in street_address:
                        street_address = "".join(street_address[:street_address.index("floor")])
                    if "Ste." in street_address:
                        street_address = "".join(street_address[:street_address.index("Ste.")])
                    if "ste." in street_address:
                        street_address = "".join(street_address[:street_address.index("ste.")])

                    try:
                        start_index = re.search(r"\d", street_address).start()
                        if start_index:
                            # print("Street Address : "+ street_address)
                            if not street_address[start_index:].isnumeric():
                                # print("Success Street Address : "+ street_address)
                                street_address = street_address[start_index:]
                    except:
                        pass

                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address[-1]))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address[-1]))

                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        country_code = "CA"

                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"

                    city = full_address[-1].split(",")[0]
                    state = full_address[-1].split(",")[1].strip().split(" ")[0]
                    latitude = soup_location.text.split("Latitude:'")[1].split("'")[0]
                    longitude = soup_location.text.split("Longitude:'")[1].split("'")[0]

                    tag_hours = soup_location.find(lambda tag: (tag.name == "h2") and "Hours of Operation" == tag.text.strip()).parent
                    if tag_hours:
                        hours_of_operation = ", ".join(list(tag_hours.stripped_strings)[1:])

                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                    if str(store[2]) not in addresses and country_code:
                        addresses.append(str(store[2]))

                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                        #print("data = " + str(store))
                        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store

        if soup.find("input",{"class":"rdpPageNext","onclick":True}):
            isLast = True
        else:
            driver.find_element_by_xpath("//input [@class='rdpPageNext']").click()
        time.sleep(10)
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
