import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('toyota_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def minute_to_hours(time):
    am = "AM"
    hour = int(time/60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time/60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time/60).split(".")[1]) * 6) + " "+ am

def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []
    for zip_code in zips:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        base_url = "https://www.toyota.com"
        # logger.info("https://www.toyota.com/ToyotaSite/rest/dealerRefresh/locateDealers?zipCode=" + str(zip_code))
        r = session.get("https://www.toyota.com/ToyotaSite/rest/dealerRefresh/locateDealers?zipCode=" + str(zip_code),headers=headers)
        if "showDealerLocatorDataArea" not in r.json():
            continue
        if "dealerLocator" not in r.json()["showDealerLocatorDataArea"]:
            continue
        for store_data in r.json()["showDealerLocatorDataArea"]["dealerLocator"][0]["dealerLocatorDetail"]:
            name = store_data["dealerParty"]["specifiedOrganization"]["companyName"]["value"]
            address = store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]["lineOne"]["value"]
            if "lineTwo" in store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]:
                address = address + " " + store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]["lineTwo"]["value"]
            if address in addresses:
                continue
            addresses.append(address)
            city = store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]["cityName"]["value"]
            state = store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]["stateOrProvinceCountrySubDivisionID"]["value"]
            store_zip = store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["postalAddress"]["postcode"]["value"]
            store_id = store_data["dealerParty"]["partyID"]["value"]
            phone = store_data["dealerParty"]["specifiedOrganization"]["primaryContact"][0]["telephoneCommunication"][0]["completeNumber"]["value"]
            lat = store_data["proximityMeasureGroup"]["geographicalCoordinate"]["latitudeMeasure"]["value"]
            lng = store_data["proximityMeasureGroup"]["geographicalCoordinate"]["longitudeMeasure"]["value"]
            hours = ""
            if "hoursOfOperation" in store_data:
                store_hours = store_data["hoursOfOperation"][0]["daysOfWeek"]
                for i in range(len(store_hours)):
                    if "availabilityEndTimeMeasure" in store_hours[i]:
                        hours = hours + " " + store_hours[i]["dayOfWeekCode"] + " " + minute_to_hours(int(store_hours[i]["availabilityStartTimeMeasure"]["value"])) + " - " + minute_to_hours(int(store_hours[i]["availabilityEndTimeMeasure"]["value"]))
                    else:
                        hours = hours + " " + store_hours[i]["dayOfWeekCode"] + " closed"
            else:
                hours = "<MISSING>"
            store = []
            store.append("https://www.toyota.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append(store_id)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append("https://www.toyota.com/dealers/dealer/" + str(store_id))
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
