# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fleetfeetsports.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get("https://www.fleetfeet.com/locations", headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="location-list"]//div[@class="location"]'
        )
        for store in stores:
            temp_text = store.xpath("p/text()")

            street_address = ""
            city = ""
            state = ""
            zip = ""
            phone = ""
            raw_text = []

            is_phone_number = False
            for t in temp_text:
                curr_text = "".join(t.strip())
                if len(curr_text) > 0:
                    raw_text.append(curr_text.strip())
                    nice_phone = (
                        curr_text.strip()
                        .replace("-", "")
                        .replace("(", "")
                        .replace(")", "")
                        .replace(" ", "")
                        .strip()
                        .replace(".", "")
                        .strip()
                    )
                    if "," in nice_phone:
                        nice_phone = nice_phone.split(",")[0].strip()
                    if nice_phone.isdigit():
                        is_phone_number = True
                        phone = curr_text.strip()

            if is_phone_number:
                city_state_zip = raw_text[-2]
                street_address = ", ".join(raw_text[:-2]).strip()
            else:
                city_state_zip = raw_text[-1]
                street_address = ", ".join(raw_text[:-1]).strip()

            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
            zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

            page_url = "".join(
                store.xpath('p/a[contains(text(),"website")]/@href')
            ).strip()
            if "http" not in page_url:
                page_url = "https://www.fleetfeet.com" + page_url

            locator_domain = website
            location_name = "".join(store.xpath("h3/text()")).strip()

            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "".join(store.xpath("@data-lat")).strip()
            longitude = "".join(store.xpath("@data-lng")).strip()

            hours_of_operation = "<MISSING>"
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
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
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
