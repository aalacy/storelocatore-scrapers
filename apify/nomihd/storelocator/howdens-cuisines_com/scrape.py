# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "howdens-cuisines.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.howdens-cuisines.com"
    search_url = "https://www.howdens-cuisines.com/trouvez-le-showroom-le-plus-proche-de-chez-vous/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        stores = search_res.text.split("var marker")[1:]

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = store.split('map,title: "')[1].split('"')[0].strip()

            location_type = "<MISSING>"

            store_info_xml = (
                store.split("content: ")[1].split("});google.maps.")[0].strip()
            )

            store_sel = lxml.html.fromstring(store_info_xml)
            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store_sel.xpath("//text()")],
                )
            )

            slug = (
                location_name.replace("Howdens Cuisines ", "")
                .lower()
                .replace("é", "e")
                .strip()
            )

            page_url = base + f"/depots/howdens-cuisines-{slug}/"

            raw_address = store_info[2] + " " + store_info[3]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            if not city:
                if zip:
                    city = raw_address.split(zip)[1].strip()

            country_code = "FR"

            store_number = "<MISSING>"
            phone = store_info[-2].replace("Tél :", "").strip()

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store.split("lat:")[1].split(",")[0].strip(),
                store.split("lng:")[1].split("},")[0].strip(),
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
