# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ast

website = "kohler.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.locationsmap.kohler.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.locationsmap.kohler.com/"
    search_res = session.get(search_url, headers=headers)

    json_text = search_res.text.split("features:")[1].split("};</")[0].strip()
    json_text = (
        json_text.replace("attributes:", '"attributes":')
        .replace("OBJECTID:", '"OBJECTID":')
        .replace("Location_Key:", '"Location_Key":')
        .replace("Site_Number:", '"Site_Number":')
        .replace("Comm_Uses:", '"Comm_Uses":')
        .replace("Site_Name:", '"Site_Name":')
        .replace("Address:", '"Address":')
        .replace("City:", '"City":')
        .replace("State_or_Province:", '"State_or_Province":')
        .replace("Postal_Code:", '"Postal_Code":')
        .replace("Country:", '"Country":')
        .replace("Continent:", '"Continent":')
        .replace("Business_Unit:", '"Business_Unit":')
        .replace("Business_Sector:", '"Business_Sector":')
        .replace("Latitude:", '"Latitude":')
        .replace("Longitude:", '"Longitude":')
        .replace("Web_Approved:", '"Web_Approved":')
        .replace("geometry:", '"geometry":')
        .replace("x:", '"x":')
        .replace("y:", '"y":')
        .replace("-.", "-0.")
    )
    store_list = ast.literal_eval(json_text)

    for store in store_list:

        page_url = search_url

        locator_domain = website
        location_name = store["attributes"]["Site_Name"]

        street_address = store["attributes"]["Address"].strip()
        city = store["attributes"]["City"].strip()
        state = store["attributes"]["State_or_Province"].strip()
        zip = store["attributes"]["Postal_Code"].strip()
        country_code = store["attributes"]["Country"].strip()

        phone = "<MISSING>"

        store_number = store["attributes"]["Location_Key"]

        location_type = store["attributes"]["Business_Unit"]

        hours_of_operation = "<MISSING>"

        latitude = store["attributes"]["Latitude"]
        longitude = store["attributes"]["Longitude"]
        raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
