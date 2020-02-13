import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import geonamescache

# gc = geonamescache.GeonamesCache()
# countries = gc.get_cities()
# print countries dictionary
# print(countries)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "raw_address","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    addresses = []
    base_url = "https://fasmart.com"
    r = requests.get(
        "https://gpminvestments.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all("script",{"type":"text/javascript"})
    for d in script:
        if "wpgmaps_localize_marker_data" in d.text:
            kd=d.text.split("var wpgmaps_localize_cat_ids =")[0].split("wpgmaps_localize_marker_data = ")[1].replace("};","}")
            # .split("var wpgmaps_localize_marker_data = ")[1].replace('"}}};',"}}}")
            for data in json.loads(kd):
                for key in json.loads(kd)[data].keys():
                    full_address=(json.loads(kd)[data][key]['address'])
                    locatin_name = json.loads(kd)[data][key]['title']
                    latitude = json.loads(kd)[data][key]['lat']
                    longitude = json.loads(kd)[data][key]['lng']

                    state_list = re.findall(r' ([A-Z]{2})', str(full_address.replace(", United States","").replace("US","")))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address).replace(", United States","").replace("US","").replace(", USA",''))



                    if state_list:
                        state = state_list[-1]

                    # print(full_address)
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"
                    all_data =full_address.replace(state,'').replace(zipp,'').replace(", USA",'').replace(", United States",'').lstrip(",")

                    store = []
                    # "inaccessible"
                    # "INACCESSIBLE"
                    store.append("https://fasmart.com")
                    store.append(locatin_name)
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append("<MISSING>")  # phone
                    store.append("<MISSING>")  # location_type
                    store.append(latitude)
                    store.append(longitude)
                    store.append("<MISSING>")  # hours_of_operation
                    store.append(all_data)
                    store.append("<MISSING>")  # page_url
                    if store[-2] in addresses:
                        continue
                    addresses.append(store[-2])
                    return_main_object.append(store)
                    store = [str(x).encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]
                    store = ["<MISSING>" if x == "" or x == "  " else x for x in store]

                    yield store
                    # print("data == " + str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            # print(all_data)
                        # print(state)

    # exit()
    # # data ="action=wpgmza_datatables_sl&security=1352287db4&map_id=7&marker_array%5B%5D=2059&marker_array%5B%5D=2076&marker_array%5B%5D=2077&marker_array%5B%5D=2080&marker_array%5B%5D=2086&marker_array%5B%5D=2088&marker_array%5B%5D=2093&marker_array%5B%5D=2094&marker_array%5B%5D=2095&marker_array%5B%5D=2099&marker_array%5B%5D=2100&marker_array%5B%5D=2101&marker_array%5B%5D=2102&marker_array%5B%5D=2103&marker_array%5B%5D=2104&marker_array%5B%5D=2105&marker_array%5B%5D=2106&marker_array%5B%5D=2107&marker_array%5B%5D=2108"
    # data = "action=wpgmza_sl_basictable&security=fc0b57223a&map_id=7"
    # # data =''
    # for state in soup.find_all("a", {"name": re.compile("marker")}):
    #             data = data + "&marker_array%5B%5D=" + \
    #         state["name"].replace("marker", "")
    
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    #     "x-requested-with": "XMLHttpRequest",
    #     "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    # }

    # r = requests.post(
    #     "https://gpminvestments.com/wp-admin/admin-ajax.php", headers=headers, data=data)
    # soup = BeautifulSoup(r.text, "lxml")
    # script = soup.find_all("script",{"type":"text/javascript"})

  
    # # tag_store = soup.find_all(lambda tag: (tag.name == "script") and "wpgmaps_localize_marker_data" in tag.text.strip())
    # # print(tag_store)

    # exit()
    # for location in soup.find("div").find_all("div", recursive=False):
    #     geo_location = location.find("a", text="Directions")["gps"]
    #     latitude = geo_location.split(",")[0].strip()
    #     longitude = geo_location.split(",")[1].strip()
    #     if "" == latitude:
    #         latitude = "<MISSING>"
    #     if "" == longitude:
    #         longitude = "<MISSING>"
    #     location_details = list(location.stripped_strings)
    #     print(location_details)
    #     state_split = re.findall("([A-Z]{2})", location_details[1])
    #     if state_split:
    #         state = state_split[-1].strip()
    #         if state == "US":
    #             state = state_split[-2].strip()
    #         # if state == "SE":
    #         #     print(state_split)
    #     else:
    #         state = "<MISSING>"

    #     store_zip_split = re.findall(
    #         r"\b[0-9]{5}(?:-[0-9]{4})?\b", location_details[1])
    #     if store_zip_split:
    #         store_zip = store_zip_split[-1]
    #         if location_details[1].split(" ")[0] == store_zip:
    #             store_zip = "<MISSING>"
    #     else:
    #         store_zip = "<MISSING>"
    #     location_details[1] = location_details[1].replace(
    #         location_details[0], "").replace("\t", " ")

    #     address_list = location_details[1].split(',')
    #     if " USA" in address_list:
    #         address_list.remove(" USA")
    #     if " United States" in address_list:
    #         address_list.remove(" United States")
    #     if len(address_list) == 1:
    #         address = location.find("a", text="Directions")[
    #             "wpgm_addr_field"].split('\t')
    #         if len(address) > 3:
    #             city = address[-3].strip()
    #             street_address = " ".join(address[:-3]).strip()
    #         elif len(address) == 2:
    #             city = address[-2].strip()
    #             street_address = address[0].strip()
    #         else:
    #             if len(address[0].split("  ")) > 1:
    #                 if " " != address[0].split("  ")[-1]:
    #                     if len(address[0].split("  ")) == 3:
    #                         street_address = address[0].split("  ")[0].strip()
    #                         city = address[0].split("  ")[1].strip()
    #                     else:
    #                         if len(address[0].split("  ")[-1].split()) > 2:
    #                             city = address[0].split(
    #                                 "  ")[-1].split()[0].strip()
    #                             street_address = address[0].split("  ")[
    #                                 0].strip()
    #                         else:
    #                             city = address[0].split(
    #                                 "  ")[0].split()[-1].strip()
    #                             street_address = " ".join(address[0].split("  ")[
    #                                                       0].split()[:-1]).strip()

    #                 else:
    #                     city = address[0].split("  ")[0].split()[-3].strip()
    #                     street_address = " ".join(address[0].split("  ")[
    #                                               0].split()[:-3]).strip()
    #             else:
    #                 city = "<INACCESSIBLE>"
    #                 street_address = "<INACCESSIBLE>"
    #                 # print(address[0].split("  "))
    #                 # print(len(address[0].split("  ")))
    #                 # print("~~~~~~~~~~~~~~~~~~~~~")

    #     elif len(address_list) == 2:
    #         street_address = " ".join(" ".join(address_list).split()[
    #                                   :-2][:-1]).replace("North Pleasant", "")
    #         city = " ".join(address_list).split()[:-2][-1]
    #         if "Hill" == city:
    #             city = " ".join(" ".join(address_list).split()
    #                             [:-2][-3:]).strip()

    #     else:
    #         street_address = address_list[0].strip()
    #         city = address_list[-2].strip()

        

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
