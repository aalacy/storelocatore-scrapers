# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bata.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "Referer": "https://www.bata.cl/",
    "Origin": "https://www.bata.cl",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here

    home_req = session.get(
        "https://batacl.vtexassets.com/_v/public/assets/v1/published/bundle/public/react/asset.min.js?v=1&files=vtex.store-icons@0.18.0,IconArrowBack,IconEyeSight,IconProfile,IconMenu,IconCart&files=batacl.google-maps-custom@0.0.7,common,1,0,Googlemapscustom&files=vtex.sticky-layout@0.3.4,common,0,StickyLayout&files=batacl.countdown@0.0.1,Countdownreact&files=vtex.react-portal@0.4.1,common,0,Overlay&files=vtex.native-types@0.8.0,common,IOMessage,formatIOMessage,IOMessageWithMarkers&files=vtex.order-manager@0.11.1,common&async=2&workspace=master",
        headers=headers,
    )
    json_str = (
        "[{"
        + home_req.text.split(";var i=[{")[1].strip().split("]}}]);")[0].strip()
        + "]"
    )
    stores = json.loads(
        json_str.replace("CLIENTE:", '"CLIENTE":')
        .replace("TIENDA:", '"TIENDA":')
        .replace("REGION:", '"REGION":')
        .replace("DIRECCION:", '"DIRECCION":')
        .replace("HORARIO:", '"HORARIO":')
        .replace("lat:", '"lat":')
        .replace("lng:", '"lng":')
        .strip()
    )
    for store in stores:
        page_url = "https://www.bata.cl/tiendas"
        locator_domain = website
        location_name = store["TIENDA"]
        street_address = ", ".join(
            store["DIRECCION"].split(", Región")[0].strip().split(",")[:-1]
        ).strip()
        city = store["DIRECCION"].split(", Región")[0].strip().split(",")[-1]
        state = store["REGION"]
        zip = "<MISSING>"

        country_code = "CL"

        store_number = "<MISSING>"

        phone = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = store["HORARIO"]
        latitude = store["lat"]
        longitude = store["lng"]

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
