# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from lxml import etree

website = "tedsmontanagrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.tedsmontanagrill.com/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="featurelink"]/@href')
    for store_id in stores:
        store_req = session.get(
            "https://www.tedsmontanagrill.com/scripts/CtLocationsXmlV2.3.php?lat=0&lng=0&radius=200&sid="
            + store_id,
            headers=headers,
        )

        store_xml = etree.fromstring(store_req.text)

        page_url = search_url
        locator_domain = website
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zip = ""
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = ""

        markers = store_xml.xpath("//markers/marker")
        for marker in markers:
            latitude = marker.attrib["tmglat"]
            longitude = marker.attrib["tmglng"]
            store_number = marker.attrib["tmgid"].replace("tmg", "").strip()
            location_name = marker.attrib["tmgname"]
            street_address = marker.attrib["tmgaddress"].replace("<br>", " ").strip()
            city = marker.attrib["tmgcity"]
            state = marker.attrib["tmgstate"]
            zip = marker.attrib["tmgzip"]
            phone = marker.attrib["tmgphone"]
            hours_of_operation = marker.attrib["tmghours"]
            if "temporarily closed" in hours_of_operation:
                location_type = "temporarily closed"

        try:
            hours_of_operation = "".join(
                "; ".join(hours_of_operation.split("<br>")[1:]).strip().split("\n")
            ).strip()
            try:
                hours_of_operation = hours_of_operation.split("<")[0].strip()
            except:
                pass
        except:
            pass

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        loc_list.append(curr_list)

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
