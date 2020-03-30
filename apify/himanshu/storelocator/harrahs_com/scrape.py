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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://www.caesars.com/harrahs", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    add = []
    lat = []
    lng = []
    for location in soup.find_all("option", {'data-type': "PROPERTY"}):
        # print(location.prettify())
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        try:
            location_request = session.get(
                "https://www.caesars.com/api/v1/properties/" + location["data-propcode"], headers=headers)
            # print("https://www.caesars.com/api/v1/properties/" +
            #       location["data-propcode"])
            store_data = location_request.json()
        except:
            continue
        add.append(store_data["address"]["street"])
        lat.append(store_data["location"]["latitude"])
        lng.append(store_data["location"]["longitude"])

    #     store = []
    #     store.append("https://www.harrahs.com")
    #     store.append(store_data["name"])
    #     store.append(address["street"])
    #     if store[-1] in addresses:
    #         continue
    #     addresses.append(store[-1])
    #     if "," in address["city"]:
    #         store.append(address["city"].split(",")[0])
    #         store.append(address["city"].split(",")[1])
    #         store.append(address["zip"])
    #         store.append("CA")
    #     else:
    #         store.append(address["city"])
    #         store.append(address["state"])
    #         store.append(address["zip"])
    #         store.append("US")
    #     store.append(store_data["preferenceId"])
    #     store.append(store_data["phone"].replace(
    #         "SHOE", "") if store_data["phone"] else "<MISSING>")
    #     store.append("<MISSING>")
    #     store.append(store_data["location"]["latitude"])
    #     store.append(store_data["location"]["longitude"])
    #     hours = "<MISSING>"
    #     store.append(hours if hours else "<MISSING>")
    #     store.append("<MISSING>")
    #     print("data == " + str(store))
    #     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
    #     yield store
    r = session.get(
        "https://www.caesars.com/myrewards/casino-directory", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    p = []
    for a in soup.find("div", class_="CETPropertyLinkList").find_all("a"):
        location_name = a.text.strip()
        if "https:" not in a["href"]:
            if "harrahs-cherokee" in a["href"]:
                page_url = "https:" + a["href"]
                # print(page_url)
                # https://www.caesars.com/harrahs-cherokee
            elif "caesars-southern-indiana" in a["href"]:
                page_url = "https://www.caesars.com/" + a["href"]
        else:
            page_url = a["href"]
        if page_url in p:
            continue
        p.append(page_url)
        # print(page_url)
        try:
            r_loc = session.get(page_url, headers=headers)

            # print(page_url)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            locator_domain = "https://www.harrahs.com"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            address = list(soup_loc.find(
                "div", class_="footer-hotel-address").stripped_strings)
            if "Hotel Information" in " ".join(address):
                address.remove("Hotel Information")
            street_address = address[0].strip()
            for i in range(len(add)):
                if street_address == add[i].strip():
                    latitude = lat[i]
                    longitude = lng[i]

                # print(street_address + " " + add[i])
                # print("~~~~~~~~~~~~~~~~~`")
            city = address[1].strip().split(",")[0].strip()
            state = address[1].strip().split(",")[1].split()[0].strip()
            zipp_tag = address[1].strip()
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_tag))

            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_tag))
            if ca_zip_list:
                zipp = ca_zip_list[-1].strip()
                country_code = "CA"
            if us_zip_list:
                zipp = us_zip_list[-1].strip()
                country_code = "US"
            phone_tag = address[2].replace(
                "Tel:", "").replace("SHOE/", "").strip()
            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
            if phone_list:
                phone = phone_list[-1].strip()
                if ")" in phone:
                    phone = "(" + phone_list[-1].strip()
            else:
                phone = "<MISSING>"
        except Exception as e:
            # print(page_url)
            # https://www.caesars.com//content/cet-global/caesars-com/caesars-southern-indiana---> this can't br reached
            pass
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        # if street_address in addresses:
        #     continue
        # addresses.append(street_address)
        # print(state)
        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store

        # print(page_url)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
