# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "friendshipfoodstores.com"
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

    search_url = "https://friendshipstores.com/find-a-store"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("var infoWindowContent = ")[1]
        .strip()
        .split("]];")[0]
        .strip()
        + "]]"
    )

    markers = (
        stores_req.text.split("var markers = ")[1].strip().split("]];")[0].strip()
        + "]]"
    ).split("['")
    stores = json_text.split("['")
    for index in range(1, len(stores)):
        store_data = stores[index].split("'],")[0].strip()
        store_sel = lxml.html.fromstring(store_data)
        page_url = search_url

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="info_content_text"]/h6/text()')
        ).strip()
        if "Corporate" not in location_name:
            if location_name == "":
                location_name = "<MISSING>"

            address = "".join(
                store_sel.xpath('//div[@class="info_content_text"]/p/text()')
            ).strip()
            street_address = address.split(",")[0].strip()
            city_state = (
                markers[index]
                .split("',")[0]
                .strip()
                .replace(location_name, "")
                .strip()
                .replace("'", "")
                .strip()
            )
            street_address = street_address.replace(city_state, "").strip()
            city = city_state.rsplit(" ", 1)[0].strip()
            if "," in city:
                city = city.split(",")[0].strip()
                street_address = street_address.replace(city, "").strip()

            state = city_state.rsplit(" ")[-1].strip()
            if len(state) != 2:
                state = "<MISSING>"

            zip = address.split(",")[-1].strip()

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

            store_number = location_name.split("#")[1].strip()
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="info_content_buttons"]/a[contains(@href,"tel:")]/text()'
                )
            ).strip()

            location_type = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//a[@class="get-map-directions"]/@href')
            ).strip()
            latitude = map_link.split("destination=")[1].strip().split(",")[0].strip()
            longitude = map_link.split("destination=")[1].strip().split(",")[1].strip()

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

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
