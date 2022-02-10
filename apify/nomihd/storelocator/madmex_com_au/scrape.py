# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import time
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "madmex.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.madmex.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/xml, text/xml, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.madmex.com.au/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("wpml_lang", ""),
    ("t", str(round(time.time() * 1000))),
)


def fetch_data():
    # Your scraper here
    api_url = "https://www.madmex.com.au/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)

        api_sel = lxml.html.fromstring(api_res.text)
        stores = api_sel.xpath("//store/item")

        for store in stores:

            locator_domain = website

            location_name = "".join(store.xpath("./location//text()")).strip()

            location_type = "<MISSING>"

            raw_address = (
                "".join(store.xpath("./address//text()"))
                .strip()
                .replace("&#44;", ",")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "AU"

            phone = "".join(store.xpath("./telephone//text()"))

            page_url = "https://www.madmex.com.au/location/" + location_name
            location_name = location_name.replace("-", " ").strip()
            hour_html_str = (
                "<div>" + "".join(store.xpath("./description//text()")) + "</div>"
            )

            hour_sel = lxml.html.fromstring(hour_html_str)

            hours = list(
                filter(
                    str,
                    [x.strip() for x in hour_sel.xpath("//text()")],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .strip()
                .replace("\r\n", "")
                .replace("\n", "")
                .strip()
                .replace("day;", "day:")
                .strip()
                .replace("-;", "-")
                .strip()
            )
            if "Temporarily Closed" in hours_of_operation:
                location_type = "Temporarily Closed"

            if hours_of_operation == "TBD":
                hours_of_operation = "<MISSING>"

            store_number = "".join(store.xpath(".//storeid//text()"))

            latitude, longitude = "".join(store.xpath("./latitude//text()")), "".join(
                store.xpath("./longitude//text()")
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
