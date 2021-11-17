# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser


website = "cinnabon.co.za"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.cinnabon.co.za",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.cinnabon.co.za/store-locator"
    with SgRequests(dont_retry_status_codes=set([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath('//div[@role]//a[@data-testid="linkElement"]')

        for store in store_list:

            page_url = "".join(store.xpath("./@href"))

            locator_domain = website
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locations = store_sel.xpath("//div[h4]/..")

            for location in locations:

                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in location.xpath("./div[2]//text()")],
                    )
                )

                full_address = store_info[:-1]
                raw_address = (
                    " ".join(full_address)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )
                if "Coming Soon" in raw_address:
                    continue
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if not city:
                    city = raw_address.split(" ")[-1]

                state = formatted_addr.state
                if state and state == "North":
                    city = city + " North"
                    state = "<MISSING>"

                zip = formatted_addr.postcode

                country_code = "ZA"

                location_name = " ".join(location.xpath("./div[1]//text()")).strip()

                phone = (
                    store_info[-1]
                    .strip()
                    .replace("Tel:", "")
                    .replace("n/a", "")
                    .strip()
                )
                store_number = "<MISSING>"

                location_type = "<MISSING>"

                hours = location.xpath("./div[3]/p[position()>=3]")
                hours_list = []
                for hour in hours:
                    if len("".join(hour.xpath(".//text()")).strip()) > 0:
                        hours_list.append("".join(hour.xpath(".//text()")).strip())
                hours_of_operation = (
                    ", ".join(hours_list)
                    .strip()
                    .replace("\u200b", "")
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )

                latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
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
