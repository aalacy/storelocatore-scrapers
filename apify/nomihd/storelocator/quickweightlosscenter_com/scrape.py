# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "quickweightlosscenter.com"
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

    search_url = "https://preview.quickweightloss.net/locations-list/"
    stores_req = session.get(search_url, headers=headers)
    states = stores_req.text.split('<h2><span style="color: #e22300;"><strong>')

    for index in range(1, len(states)):
        state_name = (
            states[index].split(":", 1)[0].strip().replace("Locations", "").strip()
        )
        stores_sel = lxml.html.fromstring(states[index])
        stores = stores_sel.xpath("//p")
        for store in stores:
            if len("".join(store.xpath("span[1]/text()")).strip()) > 0:
                location_name = "".join(store.xpath("span[1]/text()")).strip()
                page_url = search_url
                locator_domain = website

                if location_name == "":
                    location_name = "<MISSING>"

                add_phone = store.xpath("text()")
                add_list = []
                for add in add_phone:
                    if len("".join(add).strip()) > 0:
                        add_list.append("".join(add).strip())

                add_list = "#".join(add_list).strip()
                street_address = ", ".join(add_list.split(",")[:-1]).strip()
                city = add_list.split(",")[-1].strip()
                if "#(" in city:
                    city = city.split("#(")[0].strip()

                state = state_name
                zip = "<MISSING>"
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
                phone = ""
                try:
                    phone = "(" + add_list.split("(")[1].strip()
                except:
                    pass

                city = city.replace(phone, "").strip()
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

                if phone == "<MISSING>":
                    phone = " ".join(city.rsplit(" ")[-2:])
                    city = city.replace(phone, "").strip()

                city = city.replace(" l", "").replace(" 1", "").strip()
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
