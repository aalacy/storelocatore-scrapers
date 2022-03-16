# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup

website = "petros.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.petros.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "lxml")
    for i in soup.find_all(
        "div",
        {
            "class": "sqs-block code-block sqs-block-code",
        },
    ):
        raw_info = list(i.stripped_strings)
        if len(raw_info) > 1:
            if "Coming Soon!" not in raw_info:
                page_url = search_url
                location_type = "<MISSING>"
                location_name = raw_info[0].strip()
                locator_domain = website
                street_address = ""
                city_state_zip = ""
                hours_of_operation = ""
                for index in range(1, len(raw_info)):
                    if ", " in raw_info[index]:
                        street_address = ", ".join(raw_info[1:index]).strip()
                        if "," in street_address:
                            street_address = street_address.split(",")[1].strip()

                        city_state_zip = raw_info[index]
                    if "Mondays" in raw_info[index] or "Open" in raw_info[index]:
                        hours_of_operation = (
                            "; ".join(raw_info[index:-1])
                            .strip()
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "-")
                            .strip()
                        )

                city = city_state_zip.split(",")[0].strip()
                state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
                country_code = "US"

                if len(location_name) <= 0:
                    location_name = city

                phone = raw_info[-1].strip()

                store_number = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

    loc_list = []
    title_list = []
    locations_temp = soup.find_all("p", {"style": "white-space:pre-wrap;"})
    titles_temp = soup.find_all("h3", {"style": "white-space:pre-wrap;"})
    for temp in locations_temp:
        if len(list(temp.stripped_strings)) > 0:
            loc_list.append(list(temp.stripped_strings))

    for temp in titles_temp:
        if len(list(temp.stripped_strings)) > 0:
            title_list.append(list(temp.stripped_strings))

    for index in range(0, len(title_list)):
        page_url = search_url
        location_type = "<MISSING>"
        raw_info = loc_list[index]
        if "Open on Game and Special Event Days" in raw_info:
            continue
        location_name = "".join(title_list[index]).strip()
        locator_domain = website
        street_address = ""
        city_state_zip = ""
        hours_of_operation = ""
        for index in range(0, len(raw_info)):
            if ", " in raw_info[index]:
                street_address = ", ".join(raw_info[:index]).strip()
                if "," in street_address:
                    street_address = street_address.split(",")[1].strip()

                city_state_zip = raw_info[index]
            if "Mondays" in raw_info[index] or "Open" in raw_info[index]:
                hours_of_operation = (
                    "; ".join(raw_info[index:-1])
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        if len(location_name) <= 0:
            location_name = city

        phone = raw_info[-1].strip()

        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
