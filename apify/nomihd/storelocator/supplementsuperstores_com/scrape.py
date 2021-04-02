# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "supplementsuperstores.com"
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

    search_url = "https://client.lifterlocator.com/maps/jsonGet/s2faction.myshopify.com?storeName=s2faction.myshopify.com&mapId=660&loadSource=initial&maxResults=10000&radius=1000000&zoom=3&address=&latitude=43.83452678223684&longitude=-46.93359375&initialView=auto&measurement=mi"
    stores_req = session.get(search_url, headers=headers)
    stores_req_2 = session.get(
        "https://supplementsuperstores.com/pages/store-locator",
        headers={
            "authority": "supplementsuperstores.com",
            "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://supplementsuperstores.com/pages/store-locator",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        },
    )
    stores_sel = lxml.html.fromstring(stores_req_2.text)

    stores_html = stores_sel.xpath('//div[@data-dropdown="locations"]//ul/li/a/@href')
    stores = json.loads(stores_req.text)
    done_locations = []
    for store in stores:
        locator_domain = website
        location_name = store["name"]
        if location_name == "":
            location_name = "<MISSING>"

        store_number = str(store["id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        desc = store["description"]
        desc_sel = lxml.html.fromstring(desc)
        page_url = "".join(desc_sel.xpath('//a[@target="_new"]/@href')).strip()
        log.info(page_url)
        done_locations.append(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.json()["page"]["body_html"])
        address = store_sel.xpath("//div[position()>1]/text()")
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        if "COMING SOON" in add_list:
            continue
        street_address = add_list[0]
        city = add_list[1].split(",")[0].strip()
        state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].split(",")[1].strip().split(" ")[-1].strip()
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

        hours_of_operation = (
            "; ".join("".join(add_list[3:]).split("\n"))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
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
        # break

    for store_url in stores_html:
        page_url = ""
        if "supplementsuperstores" not in store_url:
            page_url = "https://supplementsuperstores.com" + store_url
        else:
            page_url = store_url

        if (
            page_url.lower() not in done_locations
            and "https://supplementsuperstores.com/pages/store-locator" not in page_url
        ):
            locator_domain = website
            store_number = "<MISSING>"

            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            json_data = store_req.json()
            store_sel = lxml.html.fromstring(json_data["page"]["body_html"])
            location_name = json_data["page"]["title"]
            if location_name == "":
                location_name = "<MISSING>"

            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()
            address = store_sel.xpath("//div[position()>1]/text()")
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            if "COMING SOON" in add_list:
                continue
            street_address = add_list[0]
            city = add_list[1].split(",")[0].strip()
            state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[1].split(",")[1].strip().split(" ")[-1].strip()
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

            hours_of_operation = (
                "; ".join("".join(add_list[3:]).split("\n"))
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
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
