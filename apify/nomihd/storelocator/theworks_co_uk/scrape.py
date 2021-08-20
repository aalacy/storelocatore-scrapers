# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "theworks.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "api.woosmap.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "accept": "*/*",
    "origin": "https://www.theworks.co.uk",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.theworks.co.uk/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    current_page = 1
    while True:
        search_url = "https://api.woosmap.com/stores/search?key=woos-c51a7170-fe29-3221-a27e-f73187126d1b&lat=51.50732&lng=-0.12764746&stores_by_page=300&limit=300&page={}"
        stores_req = session.get(search_url.format(str(current_page)), headers=headers)

        current_page = json.loads(stores_req.text)["pagination"]["page"]
        total_pages = json.loads(stores_req.text)["pagination"]["pageCount"]

        stores = json.loads(stores_req.text)["features"]
        for store in stores:
            locator_domain = website
            prop = store["properties"]
            location_name = prop["name"]
            page_url = "https://www.theworks.co.uk/Store?storeId=" + prop["store_id"]
            latitude = str(store["geometry"]["coordinates"][1])
            longitude = str(store["geometry"]["coordinates"][0])
            store_number = prop["store_id"]
            street_address = ", ".join(prop["address"]["lines"]).strip()
            city = prop["address"]["city"]
            zip = prop["address"]["zipcode"]
            country_code = prop["address"]["country_code"]
            state = "<MISSING>"
            location_type = "<MISSING>"
            log.info(page_url)

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            phone = "".join(
                store_sel.xpath('//span[@itemprop="telephone"]/a/text()')
            ).strip()

            hours = store_sel.xpath('//div[@class="store-hours-usual"]/p')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('span[@class="day"]/text()')).strip()
                time = "".join(hour.xpath('span[@class="hours"]/text()')).strip()
                if len(time) > 0:
                    hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            if store_number == "":
                store_number = "<MISSING>"

            if location_name == "":
                location_name = "<MISSING>"

            country_code = "GB"

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

        if current_page == total_pages:
            break
        else:
            current_page = current_page + 1

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
