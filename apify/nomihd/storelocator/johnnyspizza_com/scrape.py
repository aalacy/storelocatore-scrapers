# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "johnnyspizza.com"
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

    search_url = "https://johnnyspizza.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//ul[@id="menu-states"]/li/a/@href')
    for state_url in states:
        stores_req = session.get(state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//a[@class="result-title"]/@href')

        for store_url in stores:
            page_url = store_url
            locator_domain = website

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = "".join(
                store_sel.xpath('//meta[@name="geo.placename"]/@content')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:street_address"]/@content'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:locality"]/@content'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:region"]/@content'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:postal_code"]/@content'
                )
            ).strip()

            country_code = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:country"]/@content'
                )
            ).strip()
            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            if country_code == "":
                country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//meta[@property="business:contact_data:phone_number"]/@content'
                )
            ).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath('//meta[@property="business:hours:day"]')
            hours_of_operation = ""
            hours_list = []
            for index in range(0, len(hours)):
                day = "".join(hours[index].xpath("@content")).strip()
                start = "".join(
                    store_sel.xpath(
                        '//meta[@property="business:hours:start"][{}]/@content'.format(
                            str(index + 1)
                        )
                    )
                ).strip()
                end = "".join(
                    store_sel.xpath(
                        '//meta[@property="business:hours:end"][{}]/@content'.format(
                            str(index + 1)
                        )
                    )
                ).strip()
                hours_list.append(day + ":" + start + "-" + end)

            hours_of_operation = ";".join(hours_list).strip()

            latitude = "".join(
                store_sel.xpath('//meta[@property="place:location:latitude"]/@content')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//meta[@property="place:location:longitude"]/@content')
            ).strip()

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
