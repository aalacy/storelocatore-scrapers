# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import json

website = "savers.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)


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

    session = SgRequests().requests_retry_session(retries=5, backoff_factor=0.3)

    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://savers.co.uk/store-finder",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    session.get("https://savers.co.uk/", timeout=(30, 30), headers=headers)

    csrf_token = session.get(
        "https://savers.co.uk/ajaxCSRFToken", timeout=(30, 30), headers=headers
    ).text
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "accept": "application/json",
        "x-csrf-token": csrf_token,
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://savers.co.uk",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "same-origin",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    coords = static_coordinate_list(radius=20, country_code=SearchableCountries.BRITAIN)
    for lat, lng in coords:
        log.info(f"Pulling stores for {lat,lng}")
        data = {
            "q": lat + "," + lng,
            "country": "GB",
            "services": "",
        }

        stores_req = session.post(
            "https://savers.co.uk/getstorelocatoraddress.json",
            timeout=(30, 30),
            data=data,
            headers=headers,
        )
        stores = json.loads(stores_req.text)["results"]
        for store in stores:
            page_url = "https://savers.co.uk" + store["url"]
            locator_domain = website
            location_name = store["name"]

            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]["line1"]
            if (
                store["address"]["line2"] is not None
                and len(store["address"]["line2"]) > 0
            ):
                street_address = street_address + "," + store["address"]["line2"]

            city = store["address"]["town"]
            state = "<MISSING>"
            zip = store["address"]["postalCode"]

            country_code = store["address"]["country"]["isocode"]

            if country_code == "":
                country_code = "<MISSING>"

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            phone = store["address"]["phone"]
            store_number = str(store["code"])
            location_type = "<MISSING>"
            if store["storeMarkedClosed"] is True:
                location_type = "Closed"

            hours = store["openingHours"]["weekDayOpeningList"]
            hours_list = []
            for hour in hours:
                time = ""
                day = hour["weekDay"]
                if hour["closed"] is True:
                    time = "Closed"
                else:
                    time = (
                        hour["openingTime"]["formattedHour"]
                        + "-"
                        + hour["closingTime"]["formattedHour"]
                    )

                hours_list.append(day + ":" + time)

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]
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
