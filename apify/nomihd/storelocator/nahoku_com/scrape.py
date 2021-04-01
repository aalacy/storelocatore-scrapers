# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "nahoku.com"
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

    search_url = "https://www.nahoku.com/store-locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@id="store-locations"]/ul/li')
    for store in stores:
        page_url = "".join(store.xpath("a/@href")).strip()
        if len(page_url) <= 0:
            page_url = "<MISSING>"
        else:
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//div[@class="slpage"]/strong[1]/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = ""
            city_state_zip = ""
            phone = ""
            temp_text = store.xpath("text()")
            add_list = []
            for temp in temp_text:
                if len("".join(temp).strip()) > 0:
                    if "Phone:" in temp:
                        phone = temp.replace("Phone:", "").strip()
                        break
                    else:
                        add_list.append("".join(temp).strip())

            street_address = ", ".join(add_list[:-1]).strip()
            city_state_zip = add_list[-1].strip()
            city = ""
            state = ""
            zip = ""
            if len(city_state_zip) > 0:
                if "," in city_state_zip:
                    city = city_state_zip.split(",")[0].strip()
                    state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                    zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
                else:
                    city = city_state_zip.split(" ")[0].strip()
                    state = city_state_zip.split(" ")[1].strip()
                    zip = city_state_zip.split(" ")[-1].strip()

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

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = ""
            hours_list = []
            try:
                hours = (
                    store_req.text.split("Hours:</strong>")[1]
                    .strip()
                    .split("</div>")[0]
                    .strip()
                    .split("<br>")
                )
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())
            except:
                pass

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()
            latitude = ""
            longitude = ""
            if len(map_link) > 0:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if hours_of_operation == "":
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
