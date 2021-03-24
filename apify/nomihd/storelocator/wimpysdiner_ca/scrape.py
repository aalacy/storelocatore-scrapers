# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as BS

website = "wimpysdiner.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://wimpysdiner.ca/our-locations/"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("var maplistScriptParamsKo =")[1]
        .strip()
        .split("};")[0]
        .strip()
        + "}"
    )
    stores = json.loads(json_text)["KOObject"][0]["locations"]

    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        soup = BS(store["simpledescription"], "lxml")
        simpledescription = soup.find_all("p")

        raw_list = []
        for index in range(0, len(simpledescription)):
            if index == 0:
                if len(list(simpledescription[index].stripped_strings)) > 0:
                    if "Open Now!" not in list(
                        simpledescription[index].stripped_strings
                    ):
                        raw_list.append(list(simpledescription[index].stripped_strings))
                else:
                    temp_address = soup.find_all("div")
                    if temp_address is not None:
                        for temp in temp_address:
                            if "Open Now!" not in list(temp.stripped_strings):
                                raw_list.append(list(temp.stripped_strings))
            else:
                temp_data = list(simpledescription[index].stripped_strings)
                if len(temp_data) > 0:
                    if "Open Now!" not in temp_data:
                        raw_list.append(temp_data)

        if len(raw_list) == 1:
            temp_hours = soup.find("h2")
            if temp_hours is not None:
                if len(list(temp_hours.stripped_strings)) > 0:
                    raw_list.append(list(temp_hours.stripped_strings))
        elif len(raw_list) <= 0:
            raw_list.append([])
            temp_hours = soup.find("h2")
            if temp_hours is not None:
                if len(list(temp_hours.stripped_strings)) > 0:
                    raw_list.append(list(temp_hours.stripped_strings))

        phone = ""
        location_name = (
            location_name.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        street_address = ""
        if "-" in location_name:
            street_address = location_name.split("-")[1].strip()
        else:
            if "  " in location_name:
                street_address = location_name.split("  ")[1].strip()

        city = ""
        state = ""
        zip = ""
        hours_of_operation = ""
        secondary_hours = ""
        address_section = raw_list[0]

        city_state_zip = ""
        city_state_zip_index = 0
        for index in range(0, len(address_section)):
            if (
                len(address_section[index].split("-")) == 3
                or "(" in address_section[index]
                or len(address_section[index].split(".")) == 3
            ):
                if (
                    "am" not in address_section[index]
                    or "pm" not in address_section[index]
                ):
                    phone = address_section[index]
            elif ", " in address_section[index]:
                city_state_zip = (
                    address_section[index]
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", " ")
                    .strip()
                )
                city_state_zip_index = index
            if "am" in address_section[index] or "pm" in address_section[index]:
                secondary_hours = address_section[index]

        if len(city_state_zip) > 0:
            city = city_state_zip.split(",")[0].strip().replace("Unit #2", "").strip()
            if len(city_state_zip.split(",")) == 3:
                state = city_state_zip.split(",")[1].strip()
                zip = city_state_zip.split(",")[-1].strip()
            else:
                if len(city_state_zip.split(",")[1].strip().split(" ")) > 1:
                    state = (
                        city_state_zip.split(",")[1].strip().split(" ", 1)[0].strip()
                    )
                    zip = city_state_zip.split(",")[1].strip().split(" ", 1)[-1].strip()
                else:
                    state = city_state_zip.split(",")[1].strip()

        if zip == "":
            try:
                zip = address_section[city_state_zip_index + 1]
            except:
                pass

        if street_address == "":
            if len(address_section) > 0:
                street_address = address_section[0].strip()

        if "-" in street_address:
            phone = street_address
            street_address = "<MISSING>"

        if len(raw_list) > 1:
            if "Delivery available at this location click here!" not in raw_list[-1]:
                hours_of_operation = (
                    "; ".join(raw_list[-1])
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", " ")
                    .strip()
                )
            else:
                hours_of_operation = secondary_hours
        else:
            hours_of_operation = secondary_hours

        if phone == "":
            if len(raw_list) > 1:
                for index in range(0, len(raw_list[1])):
                    if (
                        len(raw_list[1][index].split("-")) == 3
                        or "(" in raw_list[1][index]
                        or len(raw_list[1][index].split(".")) == 3
                    ):
                        if (
                            "am" not in raw_list[1][index]
                            or "pm" not in raw_list[1][index]
                        ):
                            phone = raw_list[1][index]

        if len(raw_list) > 1:
            if zip == "" or zip == "<MISSING>":
                zip = raw_list[1][0].strip()
                if "am" in zip or "pm" in zip or "-" in zip:
                    zip = "<MISSING>"

        if "-" in zip:
            zip = "<MISSING>"

        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

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
