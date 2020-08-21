import csv
import sys
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import usaddress as usd
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
import sgzip

session = SgRequests()

tm={
   'Recipient': 'recipient',
   'AddressNumber': 'address1',
   'AddressNumberPrefix': 'address1',
   'AddressNumberSuffix': 'address1',
   'StreetName': 'address1',
   'StreetNamePreDirectional': 'address1',
   'StreetNamePreModifier': 'address1',
   'StreetNamePreType': 'address1',
   'StreetNamePostDirectional': 'address1',
   'StreetNamePostModifier': 'address1',
   'StreetNamePostType': 'address1',
   'BuildingName': 'address1',
   'CornerOf': 'address1',
   'IntersectionSeparator': 'address1',
   'LandmarkName': 'address1',
   'USPSBoxGroupID': 'address1',
   'USPSBoxGroupType': 'address1',
   'OccupancyType': 'address1',
   'OccupancyIdentifier': 'address1',
   'PlaceName': 'city',
   'StateName': 'state',
   'ZipCode': 'zip_code',
}

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Authorization": "Bearer d168a942b4814ef725c58d116dd157544b1101864315194cf3cc1c51735ad459",
    }
    base_url = "https://www.aesop.com"

    addresses123 = []
    op = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    # current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()

    while coord:
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        zipcode = ''
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        # lat = -42.225
        # lng = -42.225
        # zip_code = 11576
        location_url = "https://cdn.contentful.com/spaces/q8kkhxjupn16/entries?locale=en&content_type=storeDetail&include=2&fields.location%5Bwithin%5D=" + \
            str(lat) + "%2C" + str(lng)
        # print(location_url)
        # print('location_url ==' +location_url)
        try:
            r = session.get(location_url, headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        k = json.loads(soup.text)['items']
        
        current_results_len = len(k)
        for i in k:
            city = ''
            if "country" in i['fields']:
                country_code = i['fields']["country"]
                if country_code.strip().lstrip() == "US" or country_code.strip().lstrip() == "CA":

                    name = i['fields']['storeName']
                    
                    # print("==============================")
                    v = i['fields']['formattedAddress']
                    addr_format = usd.tag(v,tm)
                    addr = list(addr_format[0].items())
                    street_address = addr[0][1]
                    city = addr[1][1]
                    if street_address == "880 Queen Street West":
                        state = "ON"
                        zipp = "M6J-1G3"
                    else:
                        state = addr[2][1].split(",")[0]
                        try:
                            zipp = addr[3][1]
                        except IndexError:
                            zipp = "<MISSING>"
                     
                    lat = i['fields']['location']['lat']
                    lng = i['fields']['location']['lon']
                    if "phone" in i['fields']:
                        phone = i['fields']['phone'].replace("=", "+")
                    
                    tem_var = []
                    tem_var.append("https://www.aesop.com")
                    tem_var.append(name if name else "<MISSING>")
                    tem_var.append(street_address if street_address else "<MISSING>")
                    tem_var.append(city if city else "<MISSING>")
                    tem_var.append(state if state else "<MISSING>")
                    tem_var.append(zipp if zipp else "<MISSING>")
                    tem_var.append(country_code)
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(lat if lat else "<MISSING>")
                    tem_var.append(lng if lng else "<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    
                    tem_var = [x.encode('ascii', 'ignore').decode(
                        'ascii').strip() if type(x) == str else x for x in tem_var]
                    tem_var = ["<MISSING>" if x == "" else x for x in tem_var]
                    if tem_var[2] in addresses:
                        continue
                    addresses.append(tem_var[2])
                    yield tem_var
                    # print("data == " + str(tem_var))
                    # print("~~~~~~~~~~~")

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coord = search.next_coord()   # zip_code = search.next_zip()
        break
        
def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)


scrape()
