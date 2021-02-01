# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
import json

website = "stopaminit.com"
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

    search_url = "https://stopaminit.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    records = stores_sel.xpath('//div[@class="post-title"]/h2/a')
    url_dict = {}
    for rec in records:
        url_dict["".join(rec.xpath("@title")).strip().split("#")[1].strip()] = "".join(
            rec.xpath("@href")
        ).strip()

    markers = json.loads(
        stores_req.text.split("var maps = ")[1].strip().split("}];")[0].strip() + "}]"
    )[0]["markers"]

    for marker in markers:
        data = {"action": "mmm_async_content_marker", "id": str(marker["id"])}

        store_req = session.post(
            "https://stopaminit.com/wp-admin/admin-ajax.php", data=data, headers=headers
        )
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_type = "<MISSING>"

        page_url = ""
        latitude = marker["lat"]
        longitude = marker["lng"]
        store_number = ""
        location_name = "".join(store_sel.xpath("//h2/text()")).strip()
        city_state = location_name.split("#")[1].strip().split(" ", 1)[1].strip()

        try:
            location_name = (
                location_name.split("#")[0].strip()
                + " #"
                + location_name.split("#")[1].strip().split(" ")[0].strip()
            )
        except:
            pass

        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()
            if store_number in url_dict:
                page_url = url_dict[store_number]

        street_address = "".join(
            store_sel.xpath('//li[@class="adresse"]/strong/text()')
        ).strip()

        city = ""
        state = ""
        if "," in city_state:
            city = city_state.split(",")[0].strip()
            state = city_state.split(",")[-1].strip()
        else:
            city = city_state.split(" ")[0].strip()
            state = city_state.split(" ")[-1].strip()

        street_address = street_address.replace(city_state, "").strip()
        zip = street_address.split(" ")[-1].strip()
        street_address = street_address.replace(zip, "").strip()
        if "," in street_address:
            try:
                city_first_word = city.split(" ")[0].strip()
                street_address = street_address.split(city_first_word)[0].strip()
            except:
                pass

        phone = (
            "".join(store_sel.xpath('//li[@class="telephone"]/strong/a/text()'))
            .strip()
            .replace("Ph:", "")
            .strip()
        )
        hours = store_sel.xpath('//p[@class="description-marker"]/text()')
        hours_of_operation = ""
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if "hour" in "".join(hour).strip().lower():
                    hours_of_operation = (
                        "".join(hour)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "")
                        .strip()
                    )

        hours_of_operation = hours_of_operation.split("\n")[0].strip()
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
