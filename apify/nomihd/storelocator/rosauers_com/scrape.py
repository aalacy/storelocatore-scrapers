# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "rosauers.com"
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

    search_url = "https://www.rosauers.com/store-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-wrap"]/div[@class="location"]')
    for indx in range(0, len(stores)):
        page_url = (
            "https://www.rosauers.com"
            + "".join(
                stores[indx].xpath('a[contains(text(),"See More Details")]/@href')
            ).strip()
        )

        if page_url == "":
            page_url = "<MISSING>"
        locator_domain = website
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        store_number = ""
        location_name = (
            "".join(stores[indx].xpath('div[@class="location-title"]/h2/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "~")
            .strip()
        )

        address = ""
        hours_of_operation = ""
        phone = ""
        raw_text = stores[indx].xpath("p")
        for index in range(0, len(raw_text)):
            if "Address:" in "".join(raw_text[index].xpath("strong/text()")).strip():
                address = (
                    "".join(raw_text[index].xpath("text()"))
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", " ")
                    .strip()
                )

            if "Phone:" in "".join(raw_text[index].xpath("strong/text()")).strip():
                if len(phone) <= 0:
                    phone = "".join(raw_text[index].xpath("text()")).strip()

            if (
                "Store Hours:"
                in "".join(raw_text[index].xpath("strong/text()")).strip()
            ):
                hours_of_operation = "".join(raw_text[index].xpath("text()[1]")).strip()

        street_address = address.split(",")[0].strip()
        city = address.split(",")[1].strip()
        state = address.split(",")[2].strip().split(" ")[0].strip()
        zip = address.split(",")[2].strip().split(" ")[-1].strip()

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
