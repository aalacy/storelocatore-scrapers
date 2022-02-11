# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "sirloinstockade.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "Referer": "https://sirloinstockade.mx/sucursales/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}

params = (("ver", "1.0.0"),)


def fetch_data():
    # Your scraper here

    search_url = "https://sirloinstockade.mx/sucursales"
    api_url = (
        "https://sirloinstockade.mx/wp-content/themes/sirloin/js/funciones-mapa.js"
    )
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)

        stores = (
            api_res.text.split("function devolverLugares() {")[1]
            .split('jQuery("#locations-directory-btn").on("click", function(o) {')[0]
            .strip()
            .replace("return", "")
            .strip()
            .strip("}")
        ).split("}")[:-1]
        for store in stores:
            store_info = store.replace("[", "").strip() + "}"
            locator_domain = website

            page_url = search_url
            check_comment = (
                store_info.split('nombre: "')[0].strip().split(",")[1].strip()
            )
            if "//" in check_comment:
                continue
            location_name = (
                store_info.split('nombre: "')[1].strip().split('"')[0].strip()
            )

            location_type = "<MISSING>"

            phone = (
                store_info.split('tel: "')[1]
                .strip()
                .split('"')[0]
                .strip()
                .split("/")[0]
                .strip()
                .replace("Tel", "")
                .replace(":", "")
                .replace(".", "")
                .strip()
                .split(",")[0]
                .strip()
                .split("y")[0]
                .strip()
            )

            raw_address = (
                store_info.split('direccion: "')[1].strip().split('"')[0].strip()
            )
            if "Tel." in raw_address:
                if len(phone) <= 0:
                    phone = raw_address.split("Tel.")[1].strip()
                    raw_address = raw_address.split("Tel.")[0].strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = formatted_addr.city

            state = formatted_addr.state

            zip = formatted_addr.postcode
            if zip:
                zip = (
                    zip.replace("CP.", "")
                    .replace("C.P", "")
                    .replace("C.P.", "")
                    .replace("CP", "")
                    .strip()
                    .replace(".", "")
                    .strip()
                )

            country_code = "MX"

            hours_of_operation = (
                store_info.split('horario: "')[1].strip().split('"')[0].strip()
            )

            store_number = store_info.split('id: "')[1].strip().split('"')[0].strip()

            latitude, longitude = (
                store_info.split("lat:")[1].strip().split(",")[0].strip(),
                store_info.split("lng:")[1].strip().split(",")[0].strip(),
            )
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
