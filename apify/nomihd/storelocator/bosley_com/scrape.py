# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "bosley.com"
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

    search_url = "https://www.bosley.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="section text"]/a')
    addresses = stores_sel.xpath('//div[@class="section text"]/p')
    stores_list = []
    addresses_list = []
    for store in stores:
        if len("".join(store.xpath("@href")).strip()) > 0:
            stores_list.append("".join(store.xpath("@href")).strip())

    for addr in addresses:
        if len("".join(addr.xpath(".//text()")).strip()) > 0:
            addresses_list.append("".join(addr.xpath(".//text()")).strip().split("\n"))

    coord_dict = {}
    temp_cord = (
        stores_req.text.split("function initMap() {")[1]
        .strip()
        .split("function (error) {")[0]
        .strip()
        .split("var myLatLng = ")
    )
    for index in range(1, len(temp_cord)):
        coord_dict[
            temp_cord[index].split('href="')[1].strip().split('"')[0].strip()
        ] = (temp_cord[index].split(";")[0].strip())

    for index in range(0, len(stores_list)):
        page_url = stores_list[index]

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(store_sel.xpath("//h1/text()")).strip()
        if location_name == "":
            location_name = "<MISSING>"

        add_list = addresses_list[index]

        city_state_zip_index = -1
        city_state_zip = ""
        for add in range(0, len(add_list)):
            if ", " in add_list[add] and "Suite" not in add_list[add]:
                city_state_zip = add_list[add]
                city_state_zip_index = add
                break
        if city_state_zip_index == -1:
            street_address = ",".join(add_list[:-1]).replace(",,", ",").strip()
            city_state_zip = add_list[-1]
            city = city_state_zip.split(" ")[0].strip()
            state = city_state_zip.split(" ")[1].strip()
            zip = city_state_zip.split(" ")[2].strip()

        else:
            street_address = (
                ",".join(add_list[:city_state_zip_index]).replace(",,", ",").strip()
            )
            city = city_state_zip.split(",")[0].strip()
            state = (
                city_state_zip.split(",", 1)[1]
                .strip()
                .split(" ")[0]
                .strip()
                .replace(",", "")
                .strip()
            )
            zip = city_state_zip.split(",", 1)[1].strip().split(" ")[1].strip()

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
            phone = (
                store_req.text.split(' "telephone": "')[1].strip().split('"')[0].strip()
            )
        except:
            pass

        if len(phone) <= 0:
            phone = (
                "".join(
                    store_sel.xpath('//div[@class="location-info"][1]//p[3]//text()')
                )
                .strip()
                .replace("Phone:", "")
                .strip()
            )

        if len(phone) <= 0:
            phone = (
                "".join(
                    store_sel.xpath(
                        '//div[@class="page_location_map"]/div[@class="info"][1]//p[3]//text()'
                    )
                )
                .strip()
                .replace("Phone:", "")
                .strip()
            )

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        hours_list = []
        try:
            hours = (
                store_req.text.split('"openingHours": ')[1]
                .strip()
                .split("],")[0]
                .replace("[", "")
                .strip()
                .replace('"', "")
                .strip()
                .split(",")
            )

            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

        except:
            pass

        hours_of_operation = ";".join(hours_list).strip()
        if len(hours_of_operation) <= 0:
            try:
                hours_of_operation = (
                    store_req.text.split("Hours: ")[1].strip().split("<")[0].strip()
                )
            except:
                pass

        latitude = ""
        longitude = ""
        if page_url in coord_dict:
            latitude = (
                coord_dict[page_url].split("lat:")[1].strip().split(",")[0].strip()
            )
            longitude = (
                coord_dict[page_url].split("lng:")[1].strip().split("}")[0].strip()
            )

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
