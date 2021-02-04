# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "tex-mex.com"
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

    search_url = "https://tex-mex.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="col-lg-11 col-md-11 col-sm-10 col-xs-10 location-txt"]'
    )
    for store in stores:
        page_url = store.xpath('.//a[@class="readmore-btn"]/@href')
        if len(page_url) > 0:
            page_url = page_url[0]

            locator_domain = website

            location_name = "".join(store.xpath("h3//text()")).strip()

            if location_name == "":
                location_name = "<MISSING>"

            address = store.xpath('p/a[contains(@href,"/maps/")]/text()')
            if len(address) <= 0:
                address = store.xpath("p/text()")
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            print(add_list)
            street_address = add_list[0].strip()
            city = add_list[1].split(",")[-2].strip()
            state = add_list[1].split(",")[-1].strip().split(" ")[0].strip()
            zip = add_list[1].split(",")[-1].strip().split(" ")[-1].strip()
            try:
                street_address = (
                    street_address + " " + " ".join(add_list[1].split(",")[:-2]).strip()
                )
            except:
                pass

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
            phone = "".join(store.xpath('p/a[contains(@href,"tel:")]/text()')).strip()

            location_type = "<MISSING>"
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            hours = store_sel.xpath(
                '//div[@class="col-lg-9 col-md-9 col-sm-12 col-xs-12 no-padding address"]/p/text()'
            )
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            hours_of_operation = (
                "; ".join(hours_list).strip().replace("Hours: ", "").strip()
            )

            latitude = ""
            longitude = ""
            try:
                latitude = (
                    "".join(store.xpath("p/a[1]/@href"))
                    .strip()
                    .split("/@")[1]
                    .strip()
                    .split(",")[0]
                    .strip()
                )
            except:
                pass

            try:
                longitude = (
                    "".join(store.xpath("p/a[1]/@href"))
                    .strip()
                    .split("/@")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                )
            except:
                pass

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
