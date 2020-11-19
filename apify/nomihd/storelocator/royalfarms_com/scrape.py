# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "royalfarms.com"
domain = "https://www.goddardschool.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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


def get_splitted_address(address):
    add_dict = {}
    if address[0][0].isdigit():
        add_dict["street_address"] = address[0]
        add_dict["city_state_zip"] = address[1].replace(",,", ",").strip()
    else:
        if len(address) == 3:
            add_dict["street_address"] = address[0]
            add_dict["city_state_zip"] = address[1].replace(",,", ",").strip()
        else:
            add_dict["street_address"] = address[1]
            add_dict["city_state_zip"] = address[2].replace(",,", ",").strip()
    return add_dict


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    locations_resp = session.get(
        "https://royalfarms.com/location_results.asp",
        headers=headers,
    )
    locations_sel = lxml.html.fromstring(locations_resp.text)
    states = locations_sel.xpath('//select[@id="state"]' "/option[position()>1]/@value")
    for state in states:
        data = {
            "submitStore": "yes",
            "city": "",
            "state": state,
            "zip": "",
            "miles": "15",
        }

        stores_resp = session.post(
            "https://royalfarms.com/location_results.asp", data=data, headers=headers
        )

        stores_sel = lxml.html.fromstring(stores_resp.text)
        stores = stores_sel.xpath('//tr[@class="listdata"]')
        for store in stores:
            page_url = "https://royalfarms.com/location_results.asp"
            temp_address = store.xpath("td[1]/text()")
            address_mobile = [
                "".join(add).strip()
                for add in temp_address
                if len("".join(add).strip()) > 0
            ]
            location_name = "".join(store.xpath("td[1]/strong/text()")).strip()
            add_dict = get_splitted_address(address_mobile)
            street_address = "".join(add_dict["street_address"]).strip()

            city = "".join(add_dict["city_state_zip"]).strip().split(",")[0].strip()
            state = (
                "".join(add_dict["city_state_zip"])
                .strip()
                .split(",")[1]
                .strip()
                .split("\xa0")[0]
                .strip()
            )

            zip = (
                "".join(add_dict["city_state_zip"])
                .strip()
                .split(",")[1]
                .strip()
                .split("\xa0")[1]
                .strip()
            )

            store_number = location_name.replace("STORE #", "").strip()

            if location_type == "":
                location_type = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if us.states.lookup(state):
                country_code = "US"
            else:
                country_code = "CA"

            if country_code == "":
                country_code = "<MISSING>"

            phone = "".join(address_mobile[-1]).strip()
            if phone == "":
                phone = "<MISSING>"

            hours_of_operation = "".join(store.xpath("td[2]/em/text()")).strip()
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
        #     break
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
