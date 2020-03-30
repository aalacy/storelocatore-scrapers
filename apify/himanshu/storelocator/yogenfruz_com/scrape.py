import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "https://www.yogenfruz.com"
    r = session.get("https://www.yogenfruz.com/storelocator/frozen-yogurt", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "yogen fruz"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all("a"):
        if "canada" in script.text.lower() or "usa" in script.text.lower():
            country_code = script.text[:2].upper()
            r_country = session.get(script.get("href"), headers=headers)
            soup_country = BeautifulSoup(r_country.text, "lxml")
            # print(script.text+" = Country = "+script.get("href"))

            for script_country in soup_country.find_all("div", "blocks block-r-half alllocations"):
                # print(script_country.text +" = region = "+script_country.find("a").get("href"))
                r_region = session.get(script_country.find("a").get("href"), headers=headers)
                soup_region = BeautifulSoup(r_region.text, "lxml")

                for script_region in soup_region.find_all("div", "blocks block-r-half alllocations"):
                    # print(script_region.text +" = Brooks = "+script_region.find("a").get("href"))
                    r_brooks = session.get(script_region.find("a").get("href"),headers=headers)
                    #r_brooks = session.get("https://www.yogenfruz.com/storelocator/city/whitby/ontario/canada",headers=headers)

                    soup_brooks = BeautifulSoup(r_brooks.text, "lxml")

                    for script_brooks in soup_brooks.find_all("div", "container15px"):
                        location_name = script_brooks.find("a").text
                        if location_name == "":
                            location_name = "<MISSING>"
                        # print(script_brooks.find("a").text +" = Locations = "+script_brooks.find("a").get("href"))
                        # r_location = session.get(script_brooks.find("a",text="location details").get("href"),
                        # headers=headers)
                        r_location = session.get(script_brooks.find("a").get("href"), headers=headers)
                        soup_location = BeautifulSoup(r_location.text, "lxml")

                        temp_flag = ""
                        for l_data in list(soup_location.find("div", {"class": "container15px"}).stripped_strings):
                            if "address" in l_data.lower():
                                temp_flag = "address"
                                address = ""
                            elif "phone" in l_data.lower():
                                temp_flag = "phone"
                                phone = ""
                            elif "business hours:" in l_data.lower():
                                temp_flag = "business hours"
                                hours_of_operation = ""
                            elif "ucard:" in l_data.lower():
                                temp_flag = "ucard"
                            elif "mini" in l_data.lower():
                                temp_flag = "mini"
                            elif "map" in l_data.lower():
                                temp_flag = "map"
                            else:
                                if temp_flag == "address":
                                    address += l_data + ","
                                elif temp_flag == "business hours":
                                    hours_of_operation += l_data + " "
                                elif temp_flag == "phone":
                                    phone += l_data + " "
                                else:
                                    pass

                        print("~~~~~~~~~~~~~~~~~~~~~~country ==== " + script.text)
                        print("region ==== " + script_country.find("a").text)
                        print("brooks ==== " + script_region.find("a").text)
                        print("location_name ==== " + location_name)
                        print("address ==== " + address)

                        try:
                            latlong_url = soup_location.find("div", {"class": "container15px"}).find("a")["href"]
                            latitude = latlong_url.split("daddr=")[1].split(",")[0]
                            longitude = latlong_url.split("daddr=")[1].split(",")[1].split(" ")[0]
                            print("latlong_url ==== " + latlong_url)
                        except:
                            latitude = "<MISSING>"
                            longitude = "<MISSING>"
                            pass

                        street_address = address.split(",")[0]
                        print("street_address = " + street_address)
                        if ((len(address.split(",")[-2]) == 7 and country_code == "CA") or
                                (len(address.split(",")[-2]) == 5 and country_code == "US")):
                            city = address.split(",")[-4];
                            print("city = " + city)
                            state = address.split(",")[-3].split(" ")[1];
                            print("state = " + state)
                            zipp = address.split(",")[-2]
                            print("zipp = " + zipp)
                            print("latitude = " + latitude)
                            print("longitude = " + longitude)
                        else:
                            city = address.split(",")[-3];
                            print("city = " + city)
                            state = address.split(",")[-2].split(" ")[1]
                            print("state = " + state)
                            zipp = "<MISSING>"
                            print("zipp = " + zipp)
                            print("latitude = " + latitude)
                            print("longitude = " + longitude)

                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

                        return_main_object.append(store)

            #     break
            # break

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
