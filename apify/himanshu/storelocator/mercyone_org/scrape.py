import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from bs4 import NavigableString
import json
import re
import time
import random

session = SgRequests()

def get_location_detail_data(detail_page_url):
    r = session.get(detail_page_url)
    soup = BeautifulSoup(r.text, "html5lib")
    # find all the <script> tags
    for script in soup.findAll('script'):
        if isinstance(script, NavigableString):
            continue
        # see if the script contains a variable starting with "moduleInstanceData_IH_PublicDetailView"
        # the actual variable names end with a guid, such as moduleInstanceData_IH_PublicDetailView55fcda58_2419_4bec_befc_6aa4764f9860
        if "moduleInstanceData_IH_PublicDetailView" in script.text:
            # get the value of the variable, which is json
            jsonString = re.finditer(
                r'var moduleInstanceData_IH_PublicDetailView[\s\S]+?({[\s\S]+?});\s', script.text)
            for json_match in jsonString:
                data_js = json_match.group(1)
                data_py = json.loads(data_js)
                # the location details are embedded in another javascript variable
                if "EntityJsonData" in data_py['SettingsData']:
                    settings_data = json.loads(data_py['SettingsData'])
                    entity_data_string = settings_data['EntityJsonData']
                    # get just the value of that variable and parse as json
                    entity_json_string = re.finditer(
                        r'var ih_jsonLocationDetail=({[\s\S]+?});', entity_data_string)
                    for json_value in entity_json_string:
                        loc_detail_js = json_value.group(1)
                        loc_detail_py = json.loads(loc_detail_js)
                        return loc_detail_py
    return None


def get_locations_summary_data(city_url):
  r = session.get(city_url)
  soup = BeautifulSoup(r.text, "html5lib")
  # find the <script> tags
  for script in soup.findAll("script"):
    if isinstance(script, NavigableString):
      continue
    # see if the script contains a variable starting with "moduleInstanceData_IH_PublicDetailView"
    # the actual variable names end with a guid, such as moduleInstanceData_IH_PublicDetailView55fcda58_2419_4bec_befc_6aa4764f9860
    if "moduleInstanceData_IH_PublicDetailView" in script.text:
      # get the value of the variable, which is json
      jsonString = re.finditer(
        r'var moduleInstanceData_IH_PublicDetailView[\s\S]+?({[\s\S]+?});', script.text)
      for json_match in jsonString:
        data_js = json_match.group(1)
        data_py = json.loads(data_js)
        # we're looking for the one that has a NumberOfRecords key in the SettingsData field
        if 'NumberOfRecords' in data_py['SettingsData']:
          settings_data = json.loads(data_py['SettingsData'])
          return settings_data['MapItems']
  return []


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    base_url = "https://www.mercyone.org"
    r1 = session.get(
        "https://www.mercyone.org/find-a-location/", headers=headers)

    soup1 = BeautifulSoup(r1.text, "html5lib")
    for link in soup1.find("div", {"class": "col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center"}).find_all("a"):

        city_url = link['href']+"/location-results"
        if "siouxland" in link['href']:
            city_url = link['href']+"/locations-results"
        city_url += "?page=1&count=1000"

        locations = get_locations_summary_data(city_url)

        for location in locations:
            location_name = location["Title"]
            phone = location["LocationPhoneNum"]
            page_url = base_url + location["DirectUrl"]
            latitude = location["Latitude"]
            longitude = location["Longitude"]

            store_number = ""
            street_address = ""
            city = ""
            state = ""
            zip_code = ""
            location_type = ""
            hours = ""

            # get the location detail page
            time.sleep(random.random()*2)
            loc_detail = get_location_detail_data(page_url)

            if loc_detail is not None: 
              store_number = loc_detail["Id"]
              street_address = loc_detail["Address1"]
              city = loc_detail["City"]
              state = loc_detail["StateName"]
              zip_code = loc_detail["PostalCode"]
              if len(loc_detail['OrgUnitTypes']) > 0:
                location_type = loc_detail['OrgUnitTypes'][0]['OrgUnitTypeName']
              if len(loc_detail['Schedules']) > 0:
                  for day in loc_detail['Schedules']:
                      hours += ", " if len(hours) > 0 else ""
                      hours += day["Day"] + ': ' + day["Open"] + ' - ' + day["Close"]

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(
                street_address.replace("Floor", ""))
            store.append(city)
            store.append(state)
            store.append(zip_code)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)

            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

    raise SystemExit


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
