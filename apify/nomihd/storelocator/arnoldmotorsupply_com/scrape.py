# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "arnoldmotorsupply.com"
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

    urls = [
        "https://arnoldmotorsupply.com/partstores.php",
        "https://arnoldmotorsupply.com/servicecenters.php",
    ]
    for url in urls:
        stores_req = session.get(url, headers=headers)
        for line in stores_req.iter_lines():
            if "{latLng:" in line.decode("utf-8"):
                data = "".join(line.decode("utf-8")).strip()

                latitude = data.split("latLng:[")[1].strip().split(",")[0].strip()
                longitude = (
                    data.split("latLng:[")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split("]")[0]
                    .strip()
                )
                page_url = (
                    "https://arnoldmotorsupply.com"
                    + data.split('href="')[1].strip().split('"')[0].strip()
                )

                phone = (
                    data.split('<i class="fa fa-phone"></i>')[1]
                    .strip()
                    .split("<")[0]
                    .strip()
                )
                locator_domain = website

                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                location_name = "".join(
                    store_sel.xpath(
                        '//div[@class="col-md-12 text-center"]/h1[@class="alt"]/text()'
                    )
                ).strip()
                if len(location_name) > 0:
                    address = "".join(
                        store_sel.xpath('//p[@class="locationInfo"]/text()[1]')
                    ).strip()
                    city_state = "".join(
                        store_sel.xpath(
                            '//div[@class="container"]//div[@class="col-md-12 text-center"]/h2[@class="alt"]/text()'
                        )
                    ).strip()

                    street_address = "".join(address.split(",")[:-1]).strip()
                    city = city_state.split(",")[0].strip()
                    state = city_state.split(",")[1].strip()
                    street_address = street_address.replace(city, "").strip()
                    zip = address.split(",")[-1].strip().split(" ")[-1].strip()
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

                    location_type = url.split("/")[-1].replace(".php", "").strip()
                    temp_hours = store_sel.xpath('//div[@class="locationGreyBox"]')
                    hours_of_operation = ""
                    hours_list = []
                    for temp in temp_hours:
                        if "Store Hours" in "".join(temp.xpath("h6/text()")).strip():
                            hours = temp.xpath("text()")
                            for hour in hours:
                                if len("".join(hour).strip()) > 0:
                                    hours_list.append("".join(hour).strip())

                    hours_of_operation = "; ".join(hours_list).strip()

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
