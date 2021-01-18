# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "northgatemarkets.com"
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

    search_url = "https://www.northgatemarket.com/locations/getLetLongData"
    data = {"let": "32.9754859", "long": "-96.8853773", "getlanguage": "en"}
    stores_req = session.post(search_url, data=data, headers=headers)
    json_data = stores_req.text
    if json.loads(json_data)["code"] == 200:
        stores = json.loads(json_data)["markerdata"]
        stores_sel = lxml.html.fromstring(json.loads(json_data)["response"])
        stores_from_html = stores_sel.xpath('//div[@class="store-detail"]')

        stores_dict = {}

        for st_html in stores_from_html:
            store_dict = {}
            sections = st_html.xpath('.//div[@class="store-mb10"]')
            phone_from_html = ""
            hours = ""
            zip = ""
            for sec in sections:
                if (
                    "Phone"
                    in "".join(sec.xpath('p[@class="store-teg-title"]/text()')).strip()
                ):
                    phone_from_html = "".join(sec.xpath("a/strong/text()")).strip()
                if (
                    "Hours"
                    in "".join(sec.xpath('p[@class="store-teg-title"]/text()')).strip()
                ):
                    hours = "".join(sec.xpath("a/strong/text()")).strip()
                if (
                    "Address"
                    in "".join(sec.xpath('p[@class="store-teg-title"]/text()')).strip()
                ):
                    zip = (
                        "".join(sec.xpath("a/strong/text()"))
                        .strip()
                        .split(",")[-1]
                        .strip()
                    )

                store_dict["hours"] = hours
                store_dict["zip"] = zip

            stores_dict[phone_from_html] = store_dict

        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["title"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            try:
                street_address = street_address.split("/")[0].strip()
            except:
                pass

            state = "<MISSING>"
            if "," in street_address:
                try:
                    state = street_address.split(",")[-1].strip().split(" ")[0].strip()
                except:
                    pass

                street_address = street_address.split(",")[0].strip()

            city = ""
            try:
                city = location_name.split("/")[1].strip()
            except:
                try:
                    city = location_name.split("-")[-1].strip()
                except:
                    pass

            zip = ""

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

            store_number = "<MISSING>"
            phone = store["phone"]

            location_type = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lon"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            hours_of_operation = ""
            if phone in stores_dict:
                hours_of_operation = (
                    stores_dict[phone]["hours"]
                    .replace("(60+, people with disabilities, pregnant women)", ";")
                    .strip()
                )
                zip = stores_dict[phone]["zip"]

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

            if phone == "" or phone is None:
                phone = "<MISSING>"

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
