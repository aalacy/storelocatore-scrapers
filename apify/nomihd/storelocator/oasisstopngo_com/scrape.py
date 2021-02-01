# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "oasisstopngo.com"
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

    search_url = "https://oasisstopngo.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="wpb_wrapper"]/div[@class="wpb_text_column wpb_content_element "]'
    )
    for indx in range(1, len(stores)):
        page_url = search_url
        locator_domain = website
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        store_number = ""
        location_name = "".join(
            stores[indx].xpath('div[@class="wpb_wrapper"]/p/strong/text()')
        ).strip()
        if len(location_name) <= 0:
            location_name = "".join(
                stores[indx].xpath('div[@class="wpb_wrapper"]/p/b/text()')
            ).strip()

        location_name = (
            location_name.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "'")
            .strip()
        )

        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()

        add_list = []
        hours = ""
        raw_text = stores[indx].xpath('div[@class="wpb_wrapper"]/p//text()')
        for index in range(0, len(raw_text)):
            if len("".join(raw_text[index]).strip()) > 0:
                if "Hours of Operation:" in "".join(raw_text[index]).strip():
                    if "Monday" in "".join(raw_text[index]).strip():
                        hours = (
                            "".join(raw_text[index:])
                            .strip()
                            .replace("Hours of Operation:", "")
                            .strip()
                            .replace("&nbsp;", " ")
                            .strip()
                        )
                    else:
                        hours = "".join(raw_text[index + 1 :]).strip()
                    break
                else:
                    add_list.append("".join(raw_text[index]).strip())

        street_address = ""
        city = ""
        state = ""
        zip = ""
        if len(add_list) > 1:
            street_address = add_list[1].strip()
            if "," in street_address:
                street_address = (
                    street_address.split(",")[0]
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", " ")
                    .strip()
                )
                city = add_list[1].split(",")[1].strip()
                state = add_list[1].split(",")[2].strip().split(" ")[0].strip()
                zip = add_list[1].split(",")[2].strip().split(" ")[-1].strip()

        if len(add_list) > 2:
            phone = (
                add_list[2]
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", " ")
                .strip()
            )

        hours_of_operation = (
            "; ".join(hours.split("\n"))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

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

        if street_address != "<MISSING>":
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
