import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.micelisrestaurant.com"
    r = session.get('https://www.micelis.restaurant/contact', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_con = []
    for parts in soup.find_all("div", {"id": "content"}):
        for semi_part in parts.find_all("div",{"class": "vc_row wpb_row vc_row-fluid"})[1]:
            for inner_semi_part in semi_part.find_all("div",{"class":"vc_column-inner"}):
                return_object = []
                temp_storename = list(inner_semi_part.find("div",{"class":"wpb_wrapper"}).stripped_strings)
                location_name = temp_storename[0]
                street_address = temp_storename[1]
                city = temp_storename[2].split(",")[0]
                state_zip = temp_storename[2].split(",")[1]
                state = state_zip.split(" ")[1]
                store_zip = state_zip.split(" ")[2]
                phone = temp_storename[3].split(":")[1]
                hour_op = list(parts.find("div",{"class":"vc_custom_1552291095643"}).stripped_strings)
                hours_of_operation = hour_op[2] + " " +  hour_op[3]
                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(store_zip)
                return_object.append(phone)
                return_object.append(hours_of_operation)
                return_con.append(return_object)
        rs = session.get('https://www.micelis.restaurant/map-directions', headers=headers)
        soups = BeautifulSoup(rs.text, "lxml")
        i = 0
        for parts in soups.find_all("div", {"class": "wpb_animate_when_almost_visible"}):
            full_address_url = parts.find("iframe", {"width": "600"})["src"]
            geo_request = session.get(full_address_url, headers=headers)
            geo_soup = BeautifulSoup(geo_request.text, "lxml")
            for script_geo in geo_soup.find_all("script"):
                if "initEmbed" in script_geo.text:
                    geo_data = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                    lat = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                    lng = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
            return_con[i].append(lat)
            return_con[i].append(lng)
            i = i+1
        for val in return_con:
            return_object = []
            location_name = val[1]
            street_address = val[2]
            city = val[3]
            state = val[4]
            store_zip = val[5]
            phone = val[6]
            hour = val[7]
            lat = val[8]
            lng = val[9]
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("micelisrestaurant")
            return_object.append(lat)
            return_object.append(lng)
            return_object.append(hour)
            return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()


