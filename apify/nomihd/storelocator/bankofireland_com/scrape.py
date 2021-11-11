# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "bankofireland.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bankofireland.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/json",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bankofireland.com/branch-locator/125-oconnell-st/"
    search_res = session.get(search_url, headers=headers)

    json_str = (
        search_res.text.split("window.DATA_INIT = ")[1]
        .split("</script>")[0]
        .strip()
        .strip(";")
        .strip()
    )
    json_res = json.loads(json_str)

    store_list = json_res["branches"]

    for store_key in store_list.keys():

        page_url = (
            "https://www.bankofireland.com/branch-locator/"
            + store_list[store_key]["slug"]
        )

        locator_domain = website

        raw_address = (
            store_list[store_key]["address"]
            .strip()
            .replace("Bank of Ireland,", "")
            .strip()
        )

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = "<MISSING>"
        zip = (
            raw_address.split(",")[-1]
            .strip()
            .replace("Northern Ireland", "")
            .strip()
            .replace(".", "")
            .strip()
            .replace("  ", " ")
            .strip()
        )
        try:
            zip = " ".join(zip.rsplit(" ")[-2:]).strip()
        except:
            pass

        try:
            if zip[0].isalpha() is True and zip[1].isdigit() is not True:
                zip = "<MISSING>"
        except:
            pass

        if zip == "W635":
            zip = "F94 " + zip

        country_code = "IE"
        if "Northern Ireland" in raw_address:
            country_code = "GB"

        location_name = store_list[store_key]["name"].strip()

        phone = store_list[store_key]["details"]["boi_direct"]
        store_number = store_list[store_key]["post_id"]

        location_type = "<MISSING>"

        hours = store_list[store_key]["opening_hours"]["general_opening_hours"]
        hour_list = []
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            if (val := hours[day]) :
                hour_list.append(f"{day}: {val}")
            else:
                hour_list.append(f"{day}: Closed")

        hours_of_operation = "; ".join(hour_list)

        latitude, longitude = (
            store_list[store_key]["position"]["lat"],
            store_list[store_key]["position"]["lng"],
        )

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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
