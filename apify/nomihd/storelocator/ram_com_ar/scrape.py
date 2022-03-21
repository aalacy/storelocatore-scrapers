# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ram.com.ar"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://contactofca.com.ar/concesionarios/app_maps/get.php?marca=ram&data=concesionarias&id_provincia=&id_localidad=&id_concesionaria=&tipo=todos"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)
        stores = json_res

        for store in stores:

            locator_domain = website
            if store["venta"] != "1":
                continue

            location_name = store["nombre"]
            page_url = "https://contactofca.com.ar/concesionarios/index.php?marca=r"

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = store["direccion"]
            city = store["name_localidad"]
            state = store["name_provincia"]

            zip = "<MISSING>"

            country_code = "AR"

            phone = store["telefono"]
            if phone:
                phone = phone.split("/")[0].split("<br>")[0].strip()
            hours_of_operation = store["lun_a_vie"]

            store_number = store["id_concesionaria"]

            latitude, longitude = (
                store["lat"],
                store["lng"],
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
