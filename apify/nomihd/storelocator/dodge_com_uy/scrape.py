# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dodge.com.uy"
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
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.dodge.com.uy/_dcn/PuntosDeVenta.asp"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="contGenPV"]//span[@class="PunVen"]')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(store.xpath(".//h2//text()")).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(str, [x.strip() for x in store.xpath(".//h3//text()")])
            )
            street_address = (
                " ".join(store_info)
                .strip()
                .split("Teléfono:")[0]
                .split("Direccion:")[1]
                .strip()
            )

            city = "<MISSING>"
            if street_address == "Gral. Paz 1305 esq. Coimbra":
                city = "Coimbra"
                street_address = "Gral. Paz 1305 esq"

            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "UY"
            phone = (
                " ".join(store_info)
                .strip()
                .split("Teléfono:")[1]
                .split("Mail:")[0]
                .split("Fax")[0]
                .strip()
            )

            page_url = "https://www.dodge.com.uy/PuntosDeVenta/"

            hours_of_operation = "<MISSING>"

            store_number = "<MISSING>"

            map_link = "".join(
                store.xpath(".//iframe[contains(@src,'maps')]//@src")
            ).strip()

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
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
