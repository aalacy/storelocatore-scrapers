# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "betzone.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "betzone.co.uk",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://betzone.co.uk/?notificationId=63&account=terms-and-conditions-promos",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://betzone.co.uk/?notificationId=63&account=terms-and-conditions-promos"
    )

    with SgRequests() as session:
        search_res = session.get(
            "https://betzone.co.uk/api-web/get_promo_notifications_active",
            headers=headers,
        )
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//p[./a[contains(text(),"View Map")]]')

        for store in stores:

            page_url = search_url

            locator_domain = website

            location_name = (
                "".join(store.xpath("strong/text()")).strip().replace(":", "").strip()
            )

            raw_address = "".join(store.xpath("text()")).strip()

            zip = raw_address.split(",")[-1]
            raw_address = ", ".join(raw_address.split(",")[:-1]).strip()
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

            country_code = "GB"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            map_link = (
                "".join(store.xpath("a/@href"))
                .strip()
                .replace('"', "")
                .strip()
                .replace("\\", "")
                .strip()
            )
            latitude = map_link.split("/")[-1].strip().split(",")[0].strip()
            longitude = map_link.split("/")[-1].strip().split(",")[-1].strip()

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
