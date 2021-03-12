# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
from sgscrape import sgpostal as parser

website = "davidclulow.com"
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
                "raw_address",
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
        temp_list = []
        for row in data:
            temp_list.append(row)
            writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.davidclulow.com/store-finder/"
    stores_req = session.get(search_url, headers=headers)

    json_text = (
        stores_req.text.split("var maplistScriptParamsKo =")[1]
        .strip()
        .split("};")[0]
        .strip()
        + "}"
    )

    stores = json.loads(json_text)["KOObject"][0]["locations"]

    for store in stores:
        page_url = store["locationUrl"]
        if page_url == "":
            page_url = "<MISSING>"

        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        desc = store["description"]
        desc_sel = lxml.html.fromstring(desc)

        raw_address = (
            "".join(desc_sel.xpath('//div[@class="address"]/p/text()'))
            .strip()
            .replace("\n", ",")
            .strip()
        )
        if len(raw_address) <= 0:
            raw_address = (
                "".join(desc_sel.xpath('//div[@class="one_half"]/text()'))
                .strip()
                .replace("\n", ",")
                .strip()
            )
            try:
                raw_address = raw_address.split("T:")[0].strip()
            except:
                pass

        if len(raw_address) <= 0:
            raw_address = (
                "".join(desc_sel.xpath('//div[@class="one_third"]/text()'))
                .strip()
                .replace("\n", ",")
                .strip()
            )

        if len(raw_address) <= 0:
            raw_address = (
                "".join(desc_sel.xpath("//p/text()")).strip().replace("\n", ",").strip()
            )

        if ",00 " in raw_address:
            raw_address = raw_address.split(",00")[0].strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country
        if country_code is None:
            country_code = "<MISSING>"
        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(desc_sel.xpath('//div[@class="telephone"]/a/text()')).strip()
        if len(phone) <= 0:
            phone = "".join(
                desc_sel.xpath('//div[@class="one_half last"]/text()')
            ).strip()

        phone = (
            phone.encode("ascii", "replace").decode("utf-8").replace("?", "-").strip()
        )
        try:
            phone = phone.split("-")[1].strip()
        except:
            pass

        location_type = store["categories"][0]["title"]
        hours_of_operation = ""
        hours_list = []
        hours = desc_sel.xpath('//div[@class="openinghours"]//tr')
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        if len(hours) <= 0:
            try:
                hours = (
                    desc.split("Hours</h3>")[1]
                    .strip()
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                    .replace("<br />", "")
                    .strip()
                    .split("\n")
                )
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        if (
                            "New Years Day CLOSED" not in hour
                            or "Boxing Day CLOSED" not in hour
                            or "Christmas Day CLOSED" not in hour
                        ):

                            hours_list.append("".join(hour).strip())
            except:
                pass
        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
            .replace("&amp;", "&")
            .strip()
        )
        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            raw_address,
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
