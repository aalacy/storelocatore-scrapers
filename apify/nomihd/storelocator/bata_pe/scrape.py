# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bata.pe"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bata.pe",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "service-worker-navigation-preload": "true",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    home_req = session.get("https://www.bata.pe/tiendas", headers=headers)
    json_str = (
        '{"store.custom#s'
        + home_req.text.split('<script>{"store.custom#s')[1]
        .strip()
        .split("</script>")[0]
        .strip()
    )
    stores = json.loads(json_str)[
        "store.custom#store-locator/flex-layout.row#store-locator/flex-layout.col#store-locator/storeLocator"
    ]["props"]["tiendas"]
    for store in stores:
        page_url = "https://www.bata.pe/tiendas"
        locator_domain = website
        location_name = store["nombre"]
        raw_address = store["direccion"]

        street_address = "".join(raw_address.rsplit(".", 1)[0].strip())
        city = (
            raw_address.rsplit(".", 1)[1]
            .strip()
            .split("-")[0]
            .strip()
            .split("LC:")[0]
            .strip()
            .split("639,")[0]
            .strip()
        )

        state = (
            raw_address.rsplit(".", 1)[1]
            .strip()
            .split("-")[-1]
            .strip()
            .replace("L206A", "")
            .replace("1027", "")
            .strip()
        )
        zip = "<MISSING>"

        if location_name == "B MOYOBAMBA":
            street_address = raw_address.split("-")[0].strip()
            city = "<MISSING>"
            state = raw_address.split("-")[1].strip()

        country_code = "PE"

        store_number = "<MISSING>"

        phone = store["telefono"]
        location_type = "<MISSING>"
        if "apertura_tienda" in store:
            hours_of_operation = (
                store["apertura_tienda"] + " - " + store["cierre_tienda"]
            )
            hours_of_operation = "Lun-Sab: " + hours_of_operation

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
