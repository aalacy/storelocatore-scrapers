import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                        "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fire-ice.com"
    req = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"})
    soup = BeautifulSoup(req.text, "lxml")
    locationMenu = soup.find("li", {"id": "menu-item-5881"})
    locations = locationMenu.find("ul").findAll("li")
    siteTitle = soup.find("div", {"class": "header-logo fit-logo-img add-header-height logo-is-responsive logo-has-sticky"}).find("a")["title"]
    locator_domain = base_url
    location_type = siteTitle
    data = []
    for location in locations:
        row = []
        link_location = location.find("a")["href"]
        req2  = session.get(link_location, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"})
        soup2 = BeautifulSoup(req2.text, "lxml")
        city = soup2.title.text.split("-")[0]
        phoneNo = soup2.findAll("a", href=re.compile('tel'))[0]["href"].strip().split("tel:")[1]
        address = json.loads(soup2.findAll("div", {"class": "mk-advanced-gmaps"})[0]["data-advancedgmaps-config"])["places"][0]["address"]
        lat = json.loads(soup2.findAll("div", {"class": "mk-advanced-gmaps"})[0]["data-advancedgmaps-config"])["places"][0]["latitude"]
        long = json.loads(soup2.findAll("div", {"class": "mk-advanced-gmaps"})[0]["data-advancedgmaps-config"])["places"][0]["longitude"]
        zipcode=""
        state=""
        streetAddr=""
        storeNo = "<MISSING>"
        country_code = "US"
        locationName = soup2.title.text
        if "Tahoe" not in address:
            streetAddr = address.split(",")[0]
            addr_Split = address.split(" ")
            if re.match(r'^[0-9]*$', addr_Split[len(addr_Split) - 1]):
                zipcode = addr_Split[len(addr_Split) - 1]
                state = addr_Split[len(addr_Split) - 2]
            else:
                zipcode = "<MISSING>"
                state = addr_Split[len(addr_Split) - 1]
        else:
            streetAddr = address.split(".")[0]
            addr_Split = address.split(" ")
            if re.match(r'^[0-9]*$', addr_Split[len(addr_Split) - 1]):
                zipcode = addr_Split[len(addr_Split) - 1]
                state = addr_Split[len(addr_Split) - 2]
            else:
                zipcode = "<MISSING>"
                state = addr_Split[len(addr_Split) - 1]
        hoursOfOp = {}
        if soup2.find("h2", text="Breakfast") != None:
            hoursOfOp["breakfast"] = soup2.find("h2", text="Breakfast").find_next_siblings()[0].text.replace(u'\xa0', u' ').replace("\n",",")
        if soup2.find("h2", text="Brunch") != None:
            hoursOfOp["brunch"] = soup2.find("h2", text="Brunch").find_next_siblings()[0].text.replace(u'\xa0', u' ').replace("\n",",")
        if soup2.find("h2", text="Lunch") != None:
            hoursOfOp["lunch"] = soup2.find("h2", text="Lunch").find_next_siblings()[0].text.replace(u'\xa0', u' ').replace("\n",",")
        if soup2.find("h2", text="Dinner") != None:
            hoursOfOp["dinner"] = soup2.find("h2", text="Dinner").find_next_siblings()[0].text.replace(u'\xa0', u' ').replace("\n",",")
        hoursOfOp = json.dumps(hoursOfOp)
        row.append(locator_domain)
        row.append(locationName)
        row.append(streetAddr)
        row.append(city)
        row.append(state)
        row.append(zipcode)
        row.append(country_code)
        row.append(storeNo)
        row.append(phoneNo)
        row.append(location_type)
        row.append(lat)
        row.append(long)
        row.append(hoursOfOp)
        data.append(row)
    return data  

def scrape():
    data = fetch_data()
    write_output(data)
scrape()