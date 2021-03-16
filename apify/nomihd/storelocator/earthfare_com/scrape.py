# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "earthfare.com"
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

    search_url = "https://www.earthfare.com/stores/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(
        stores_req.text.split("LOCATIONS COMING SOON")[0].strip()
    )
    stores = stores_sel.xpath(
        '//div[@class="elementor-text-editor elementor-clearfix"]'
    )
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath("h3/text()")).strip()
        if len(location_name) <= 0:
            location_name = "".join(store.xpath("h5/span/text()")).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store.xpath("p/text()")
        if len("".join(address).strip()) <= 0:
            address = store.xpath("text()")

        if len("".join(address).strip()) <= 0:
            address = store.xpath("h6/text()")

        add_list = []
        phone = ""
        for add in address:
            temp_text = "".join(add.strip())
            if len(temp_text) > 0:
                if "Phone:" in temp_text or "Ph:" in temp_text:
                    if "," in temp_text:
                        try:
                            add_list.append(temp_text.split("Phone:")[0].strip())
                            phone = temp_text.split("Phone:")[1].strip()
                        except:
                            try:
                                add_list.append(temp_text.split("Ph:")[0].strip())
                                phone = temp_text.split("Ph:")[1].strip()
                            except:
                                pass

                    else:
                        phone = (
                            temp_text.replace("Phone:", "").replace("Ph:", "").strip()
                        )
                        break

                elif "(" in temp_text and ")" in temp_text:
                    phone = temp_text
                else:
                    add_list.append("".join(temp_text))

        street_address = add_list[0]
        city = add_list[1].split(",")[0].strip()
        state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
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

        location_type = "<MISSING>"
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
