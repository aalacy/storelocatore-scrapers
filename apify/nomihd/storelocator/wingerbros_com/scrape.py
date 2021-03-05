# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from lxml import etree
import json

website = "wingerbros.com"
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

    search_url = "https://wingerbros.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang="
    stores_req = session.get(search_url, headers=headers)
    stores_sel = etree.fromstring(stores_req.text)
    stores = stores_sel.xpath("//store/item")
    for store in stores:
        page_url = ""
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

        for child in store:
            if child.tag == "latitude":
                latitude = child.text
            if child.tag == "longitude":
                longitude = child.text
            if child.tag == "storeId":
                store_number = child.text
            if child.tag == "exturl":
                page_url = child.text
            if child.tag == "telephone":
                phone = child.text
            if child.tag == "location":
                location_name = child.text.replace("&amp;", "&").strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        for js in json_list:
            if "LocalBusiness" in js:
                json_data = json.loads(js)

                street_address = json_data["address"]["streetAddress"]
                city = json_data["address"]["addressLocality"]
                state = json_data["address"]["addressRegion"]
                zip = json_data["address"]["postalCode"]

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

        sections = store_sel.xpath(
            '//div[@class="wpb_text_column wpb_content_element "]/div[@class="wpb_wrapper"]/p'
        )

        hours_list = []
        for index in range(0, len(sections)):
            if (
                "Restaurant Hours"
                in "".join(sections[index].xpath("strong/text()")).strip()
            ):
                days = sections[index + 1].xpath("text()")
                time = sections[index + 1].xpath("span/text()")
                for index in range(0, len(days)):
                    if len("".join(days[index]).strip()) > 0:
                        hours_list.append(
                            "".join(days[index] + ":" + time[index])
                            .strip()
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "-")
                            .strip()
                        )
                break

        hours_of_operation = "; ".join(hours_list).strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

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
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
