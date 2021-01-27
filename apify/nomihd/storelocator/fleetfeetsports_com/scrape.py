# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "fleetfeetsports.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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
    stores_req = session.get("https://www.fleetfeet.com/locations", headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-list"]//div[@class="location"]')
    for store in stores:
        temp_text = store.xpath("p/text()")

        street_address = ""
        city = ""
        state = ""
        zip = ""
        phone = ""
        raw_text = []

        is_phone_number = False
        for t in temp_text:
            curr_text = "".join(t.strip())
            if len(curr_text) > 0:
                raw_text.append(curr_text.strip())
                nice_phone = (
                    curr_text.strip()
                    .replace("-", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace(" ", "")
                    .strip()
                    .replace(".", "")
                    .strip()
                )
                if "," in nice_phone:
                    nice_phone = nice_phone.split(",")[0].strip()
                if nice_phone.isdigit():
                    is_phone_number = True
                    phone = curr_text.strip()

        if is_phone_number:
            city_state_zip = raw_text[-2]
            street_address = ", ".join(raw_text[:-2]).strip()
        else:
            city_state_zip = raw_text[-1]
            street_address = ", ".join(raw_text[:-1]).strip()

        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
        zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

        page_url = "".join(store.xpath('p/a[contains(text(),"website")]/@href')).strip()
        if "http" not in page_url:
            page_url = "https://www.fleetfeet.com" + page_url

        if page_url == "":
            page_url = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath("h3/text()")).strip()

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        if phone == "":
            phone = "<MISSING>"

        country_code = ""
        if us.states.lookup(state):
            country_code = "US"

        if country_code == "":
            country_code = "<MISSING>"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()

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
