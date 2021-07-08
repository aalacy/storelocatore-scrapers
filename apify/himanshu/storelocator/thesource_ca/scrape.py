import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from lxml import etree
import json


session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "page_url",
                "locator_domain",
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    }

    r = session.get(
        "https://www.thesource.ca/en-ca/store-finder?latitude=43.0&longitude=-79.0&q=&popupMode=false&show=All",
        headers=headers,
    )
    return_main_object = []
    dom = etree.HTML(r.text)
    number_page = int(dom.xpath('//span[@class="maxNumberOfPages"]/text()')[0])
    for i in range(number_page):
        page_request = session.get(
            "https://www.thesource.ca/en-ca/store-finder?latitude=43.0&longitude=-79.0&q=&popupMode=false&page="
            + str(i)
            + "&show=All",
            headers=headers,
        )
        page_soup = BeautifulSoup(page_request.text, "lxml")
        geo_locations = page_soup.find("div", {"id": "map_canvas"})["data-stores"]
        location_list = json.loads(geo_locations)
        for location in page_soup.find_all(
            "tr", {"class": "storeItem store-result-row"}
        ):
            name = location.find("a").text
            address = list(location.find("ul").stripped_strings)
            address = address if address else "<MISSING>"
            phone = location.find("p").text.strip()
            phone = phone if phone else "<MISSING>"
            if location.find("td", {"class": "hours"}) is None:
                continue
            hours = " ".join(
                list(location.find("td", {"class": "hours"}).stripped_strings)
            )
            hours = hours if hours else "<MISSING>"
            for key in location_list:
                if name == location_list[key]["name"]:
                    lat = location_list[key]["latitude"]
                    if lat == "0.0":
                        lat = "<MISSING>"
                    lng = location_list[key]["longitude"]
                    if lng == "0.0":
                        lng = "<MISSING>"
                    store_id = location_list[key]["id"]
                    del location_list[key]
                    break
            store = []
            store.append("https://www.thesource.ca")
            store.append("https://www.thesource.ca")
            store.append(name)
            store.append(" ".join(address[0:-2]))
            store.append(address[-2].split(",")[0])
            store.append(address[-2].split(",")[-1])
            if len(address[-1]) == 6:
                store.append(address[-1][0:3] + " " + address[-1][3:])
            else:
                store.append(address[-1])
            store.append("CA")
            store.append(store_id)
            store.append(phone)
            store.append("the source")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
