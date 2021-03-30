import csv
import json
from lxml import etree
from urllib import parse

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
    scraped_items = []

    DOMAIN = "huntsvillehospital.org"
    start_urls = [
        "https://www.zeemaps.com/emarkers?g=995509&k=REGULAR&e=true",
        "https://www.zeemaps.com/emarkers?g=988466&k=REGULAR&e=true",
        "https://www.zeemaps.com/emarkers?g=985453&k=REGULAR&e=true",
        "https://www.zeemaps.com/emarkers?g=988421&k=REGULAR&e=true",
        "https://www.zeemaps.com/emarkers?g=995996&k=REGULAR&e=true",
        "https://www.zeemaps.com/emarkers?g=991008&k=REGULAR&e=true",
    ]

    cat_dict = {
        "991008": "Campus Map",
        "995509": "Hospitals & Affiliates",
        "988466": "HH Phycisian Offices",
        "985453": "Imaging Locations",
        "988421": "Lab Patient Service Centers",
        "995996": "Other Locations",
    }

    for url in start_urls:
        response = session.get(url)
        data = json.loads(response.text)

        for poi in data:
            poi_url = "<MISSING>"
            loc_id = poi["id"]
            cat_id = parse.parse_qs(parse.urlparse(url).query)["g"][0]
            loc_url = f"https://www.zeemaps.com/etext?g={cat_id}&j=1&sh=&_dc=0.015354962829809748&eids=[{loc_id}]&emb=1&g={cat_id}"
            loc_response = session.get(loc_url)
            loc_data = json.loads(loc_response.text)

            poi_name = loc_data["title"]
            poi_name = poi_name if poi_name else "<MISSING>"
            street = loc_data["ad"]["street"]
            street = street if street else "<MISSING>"
            city = loc_data["ad"]["city"]
            city = city if city else "<MISSING>"
            state = loc_data["ad"]["state"]
            state = state if state else "<MISSING>"
            zip_code = loc_data["ad"]["postcode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = loc_data["ad"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            poi_number = loc_data["eid"]
            poi_number = poi_number if poi_number else "<MISSING>"
            phone = "<MISSING>"
            if loc_data["t"]:
                poi_html = etree.HTML(loc_data["t"])
                phone = poi_html.xpath('//span[@class="phone"]/text()')
                phone = phone[0] if phone else "<MISSING>"
                poi_url = poi_html.xpath("//a/@href")
                poi_url = poi_url[0] if poi_url else "<MISSING>"
            poi_type = cat_dict[cat_id]
            latitude = loc_data["lat"]
            longitude = loc_data["lng"]

            poi_html = etree.HTML(loc_data["t"])
            hoo = []
            if poi_html:
                hoo = [
                    elem.strip() for elem in poi_html.xpath("//text()") if "p.m" in elem
                ]
            hoo = " ".join(hoo).replace("\n", " ") if hoo else "<MISSING>"

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
            if poi_number not in scraped_items:
                scraped_items.append(poi_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
