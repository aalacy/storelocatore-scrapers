# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mambo.com.br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.mambo.com.br/file/v776154062911976682/widget/MBNossasLojas/js/mb-nossas-lojas.min.js?bust=22.1.4"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = (
            search_res.text.split("storeOptions:t.observable(")[1]
            .split("),onLoad")[0]
            .strip()
        )
        json_str = (
            json_str.replace("image:", '"image":')
            .replace("name:", '"name":')
            .replace("map:", '"map":')
            .replace("address:", '"address":')
            .replace("cep:", '"cep":')
            .replace("county:", '"county":')
            .replace("hourWeek:", '"hourWeek":')
            .replace("hourWeekend:", '"hourWeekend":')
            .replace("phone:", '"phone":')
            .replace("imageGerente:", '"imageGerente":')
            .replace("gerenteName:", '"gerenteName":')
        )
        stores = json.loads(json_str)

        for store in stores:

            locator_domain = website
            page_url = "https://www.mambo.com.br/nossas-lojas"

            location_name = store["name"].strip()

            location_type = "<MISSING>"

            raw_address = store["address"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            if not state:
                state = store["county"]
            zip = formatted_addr.postcode
            if not zip:
                zip = store["cep"]

            country_code = "BR"

            store_number = "<MISSING>"
            phone = store["phone"]

            hours_of_operation = store["hourWeek"] + ";" + store["hourWeekend"]

            map_link = store["map"]
            latitude, longitude = get_latlng(map_link)

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
