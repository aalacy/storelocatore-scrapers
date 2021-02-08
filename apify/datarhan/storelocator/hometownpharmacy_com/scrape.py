import csv
import json
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "hometownpharmacy.com"
    start_url = "https://hometownpharmacy.com/locations"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {
        "searchname": "",
        "searchzip": "Michigan United States 48801",
        "task": "search",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "157",
        "zoom": "7",
        "format": "json",
        "geo": "",
        "latitude": "",
        "longitude": "",
        "limitstart": "0",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["features"]:
        poi_name = poi["properties"]["name"]
        if poi["properties"]["url"]:
            poi_url = urljoin(start_url, poi["properties"]["url"])
        else:
            poi_url = "<MISSING>"
        if not poi["properties"]["fulladdress"]:
            continue
        add_html = etree.HTML(poi["properties"]["fulladdress"])
        raw_address = add_html.xpath("//text()")

        street = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[-1]
        zip_code = raw_address[2].split()[-1]
        country_code = " ".join(raw_address[2].split()[:2])
        poi_number = poi["id"]
        phone = raw_address[3]
        poi_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][0]
        longitude = poi["geometry"]["coordinates"][1]

        hoo = ""
        if poi_url != "<MISSING>":
            loc_response = session.get(poi_url, headers=headers)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath('//span[i[@class="mml-calendar"]]//text()')
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
