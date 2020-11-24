from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import re
import json
import time
import csv

logger = SgLogSetup().get_logger("merrell_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    urls = [
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=Outlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat=19.63723868607574&map_center_lng=-90.52528000000007&map_distance_diag=1448.3008429633721&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=san+fran&zoom_level=5",
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=Merrell&inline=1&show_links_in_list=&parent_domain=&map_center_lat=19.025074077515313&map_center_lng=-90.53330000000011&map_distance_diag=2840.6292207500674&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4",
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=work&inline=1&show_links_in_list=&parent_domain=&map_center_lat=19.025074077515313&map_center_lng=-90.53330000000011&map_distance_diag=2840.6292207500674&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4",
    ]
    for url in urls:
        # url = "https://merrell.locally.com/store/52316/merrell-outlet-silver-sands-premium"
        r = session.get(url, headers=headers, verify=False)
        site = json.loads(r.text)
        data_list = site["markers"]
        for store in data_list:
            title = store["name"]
            street = store["address"]
            city = store["city"]
            state = store["state"]
            zipcode = store["zip"]
            tel = store["phone"]
            lat = store["lat"]
            longt = store["lng"]
            storeid = store["id"]
            storelink = "https://merrell.locally.com/store/" + str(storeid)
            # phone = phonenumbers.parse(tel, 'US')
            phone = tel.lstrip("+1")

            r = session.get(storelink, headers=headers, verify=False)
            subsoup = BeautifulSoup(r.text, "html.parser")
            storehours = "<MISSING>"
            if subsoup.find("div", {"class": "landing-header-hours-inner"}):
                storehours = subsoup.find(
                    "div", {"class": "landing-header-hours-inner"}
                ).findAll("span")
                storehours = " ".join([str(elem.text) for elem in storehours])
            if len(storehours) == 0:
                storehours = "<MISSING>"
            data.append(
                [
                    "https://merrell.locally.com/",
                    storelink,
                    title,
                    street,
                    city,
                    state,
                    zipcode,
                    "US",
                    storeid,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    storehours,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
