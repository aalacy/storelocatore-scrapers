# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "pmpediatrics.com"
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

    search_url = "https://pmpediatrics.com/patient-resources/find-care-now/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[contains(@class,"location_block")]')
    for store in stores:
        locator_domain = website
        location_name = "".join(
            store.xpath('.//div[@class="content"]/h4/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store.xpath(
                './/div[@class="content"]/span[@class="slp_result_address slp_result_street"]/text()'
            )
        ).strip()

        street_2 = "".join(
            store.xpath(
                './/div[@class="content"]/span[@class="slp_result_address slp_result_street2"]/text()'
            )
        ).strip()

        if len(street_2) > 0:
            street_address = street_address + ", " + street_2

        city_state_zip = "".join(
            store.xpath(
                './/div[@class="content"]/span[@class="slp_result_address slp_result_citystatezip"]/text()'
            )
        ).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip()
        zip = city_state_zip.split(",")[-1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(
            store.xpath(
                './/div[@class="content"]/span[@class="slp_result_address slp_result_phone"]/a/text()'
            )
        ).strip()

        location_type = "<MISSING>"
        page_url = "".join(store.xpath('.//div[@class="buttons"]/a[1]/@href')).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if "coming soon" in store_req.text.lower():
            location_type = "Coming Soon"

        temp_hours = store_sel.xpath('//div[@id="loc_address"]/p')
        hours_of_operation = ""
        for temp in temp_hours:
            text = "".join(temp.xpath(".//text()")).strip()
            if "Office hours" in text or "Office Hours" in text:
                hours_of_operation = (
                    text.strip()
                    .replace("Office hours:", "")
                    .replace("Office Hours:", "")
                    .replace(
                        "Urgent Care & COVID Testing  Exclusively for children and their accompanying parent/caregiver",
                        "",
                    )
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

        if len(hours_of_operation) <= 0:
            hours_of_operation = (
                "".join(
                    store_sel.xpath(
                        '//div[@id="loc_address"]//span[@style="font-weight: 400;"]/text()'
                    )
                )
                .strip()
                .replace("Office hours:", "")
                .replace("Office Hours:", "")
                .replace(
                    "Urgent Care & COVID Testing  Exclusively for children and their accompanying parent/caregiver",
                    "",
                )
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

        if len(hours_of_operation) <= 0:
            for temp in temp_hours:
                text = "".join(temp.xpath("text()")).strip().lower()
                if (
                    "monday" in text
                    or "tuesday" in text
                    or "wednesday" in text
                    or "thursday" in text
                    or "friday" in text
                    or "saturday" in text
                    or "sunday" in text
                    or "am" in text
                    or "pm" in text
                ):
                    hours_of_operation = (
                        "".join(temp.xpath("text()"))
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )

        if (
            "PM Pediatrics" in hours_of_operation
            or "Our offices remain" in hours_of_operation
        ):
            hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
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
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
