# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tudorsbiscuitworld.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "http://tudorsbiscuitworld.com/Locations.aspx"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = stores_req.text.split("BasicGoogleMaps.push({'cont':'")
        coordinates = stores_req.text.split(
            "p_lt_ctl03_pageplaceholder_p_lt_ctl01_BasicGoogleMaps_map, "
        )
        for index in range(1, len(stores)):
            store_data = (
                stores[index].split("'});")[0].strip().replace('\\"', '"').strip()
            )
            store_sel = lxml.html.fromstring(store_data)
            page_url = search_url
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//span[@class="Header"]/a/text()')
            ).strip()
            raw_text = store_sel.xpath("//span/text()")
            raw_list = []
            for raw in raw_text:
                if len("".join(raw).strip()) > 0:
                    raw_list.append("".join(raw).strip())

            formatted_addr = parser.parse_address_usa(", ".join(raw_list[:-2]))
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "US"

            phone = raw_list[-2].strip()
            hours_of_operation = raw_list[-1].strip()
            store_number = "<MISSING>"

            latitude = coordinates[index].split(",")[0].strip()
            longitude = coordinates[index].split(",")[1].strip()

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
                raw_address=", ".join(raw_list[:-2]),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
