import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rogys_com')





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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    logger.info("soup ===  first")

    base_url = "https://www.rogys.com"
    r = session.post("https://www.rogys.com/wp-admin/admin-ajax.php", headers=headers,
                      data="action=get_location_data&geolocation_data=&miles=5000&zip=61614")
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "rogys"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    json_data = r.json()
    logger.info("data ==== " + str(len(json_data['search_results']['current_blog_locations'])))

    # current_brand_locations = []
    content_parsing = "action=get_brand_results_list&"
    index = 0
    for location in json_data['search_results']['current_blog_locations']:
        content_parsing += "current_brand_locations[" + str(index) + "][id]=" + location["id"] + "&" \
                           + "current_brand_locations[" + str(index) + "][blog_id]=" + location["blog_id"] + "&" \
                           + "current_brand_locations[" + str(index) + "][post_id]=" + location["post_id"] + "&" \
                           + "current_brand_locations[" + str(index) + "][lat]=" + location["lat"] + "&" \
                           + "current_brand_locations[" + str(index) + "][lng]=" + location["lng"] + "&" \
                           + "current_brand_locations[" + str(index) + "][zip]=" + location["zip"] + "&" \
                           + "current_brand_locations[" + str(index) + "][city]=" + location["city"] + "&" \
                           + "current_brand_locations[" + str(index) + "][state]=" + location["state"] + "&" \
                           + "current_brand_locations[" + str(index) + "][distance]=" + location["distance"] + "&"
        index += 1

    index = 0
    for location in json_data['search_results']['other_blog_locations']:
        content_parsing += "other_brand_locations[" + str(index) + "][id]=" + location["id"] + "&" \
                           + "other_brand_locations[" + str(index) + "][blog_id]=" + location["blog_id"] + "&" \
                           + "other_brand_locations[" + str(index) + "][post_id]=" + location["post_id"] + "&" \
                           + "other_brand_locations[" + str(index) + "][lat]=" + location["lat"] + "&" \
                           + "other_brand_locations[" + str(index) + "][lng]=" + location["lng"] + "&" \
                           + "other_brand_locations[" + str(index) + "][zip]=" + location["zip"] + "&" \
                           + "other_brand_locations[" + str(index) + "][city]=" + location["city"] + "&" \
                           + "other_brand_locations[" + str(index) + "][state]=" + location["state"] + "&" \
                           + "other_brand_locations[" + str(index) + "][distance]=" + location["distance"] + "&"
        index += 1
    content_parsing + "post_id:483"

    logger.info(str(index) + " ====== " + content_parsing)

    r1 = session.post("https://www.rogys.com/wp-admin/admin-ajax.php", headers=headers,
                       data=content_parsing)

    content_parsing = content_parsing.replace("get_brand_results_list", "get_nonbrand_results_list")
    r2 = session.post("https://www.rogys.com/wp-admin/admin-ajax.php", headers=headers,
                       data=content_parsing)

    soup = BeautifulSoup(r1.text + r2.text, "lxml")

    # logger.info("data ==== "+ str(soup))

    for script in soup.find_all("div", {"class": "col-xs-12 result-info-wrap"})[:-1]:
        address_list = list(script.stripped_strings)

        if 'Contact' in address_list:
            address_list.remove('Contact')

        if 'Go to School Page' in address_list:
            address_list.remove('Go to School Page')

        map_location = script.find('ul', {'class': 'result-info'}).find('a')['href']

        if len(map_location.split("&sll=")) > 1:
            latitude = map_location.split("&sll=")[1].split("&")[0].split(",")[0]
            longitude = map_location.split("&sll=")[1].split("&")[0].split(",")[1]
        elif len(map_location.split("/@")) > 1:
            latitude = map_location.split("/@")[1].split(",")[0]
            longitude = map_location.split("/@")[1].split(",")[1]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        age_index = [i for i, s in enumerate(address_list) if 'Ages:' in s]
        schedule_index = [i for i, s in enumerate(address_list) if 'schedule a visit' in s.lower()]
        enrolled_index = [i for i, s in enumerate(address_list) if 'enrolled families' in s.lower()]

        logger.info("address_list === " + str(address_list))
        logger.info("enrolled_index === " + str(enrolled_index))

        zipp = address_list[age_index[0] - 1]
        state = address_list[age_index[0] - 2]
        city = address_list[age_index[0] - 4]
        street_address = address_list[age_index[0] - 5]
        location_name = address_list[age_index[0] - 6]
        phone = address_list[schedule_index[0] + 1]

        if len(enrolled_index) > 0:
            hours_of_operation = ",".join(address_list[enrolled_index[0] + 2:])
        else:
            hours_of_operation = ",".join(address_list[schedule_index[0] + 2:])
        # logger.info("location_url === " + map_location)
        # logger.info("indices === " + str(address_list[age_index[0]]))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()