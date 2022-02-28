# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "acehotel.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://acehotel.com/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//ul[@class="locations-nav"]/li')

        contact_page = "https://acehotel.com/contact/"
        contact_res = session.get(contact_page, headers=headers)
        contact_sel = lxml.html.fromstring(contact_res.text)

        for store in stores:

            location_name = " ".join(store.xpath(".//text()")).strip()
            if "Coming soon" in location_name:
                continue

            page_url = "".join(store.xpath(".//@href")).strip()
            if page_url[-1] != "/":
                page_url = page_url + "/"

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            if "Coming soon:" in store_res.text:
                log.info("ignored")
                continue
            locator_domain = website

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in contact_sel.xpath(
                            f'//div[contains(@class,"text-single-content")]//span[b[contains(text(),"{location_name}")]]/..//text()'
                        )
                    ],
                )
            )
            if len(store_info) <= 0:
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in contact_sel.xpath(
                                f'//div[contains(@class,"text-single-content")]//span[strong[contains(text(),"{location_name}")]]/..//text()'
                            )
                        ],
                    )
                )
            raw_address = " ".join(store_info[1:]).split("Tel")[0].strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            if not city:
                city = location_name.strip()
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = formatted_addr.country
            if not country_code:
                country_code = "US"

            store_number = "<MISSING>"

            phone = contact_sel.xpath(
                f'//div[contains(@class,"text-single-content")]//span[b[contains(text(),"{location_name}")]]/..//a[contains(@href,"tel:")]//text()'
            )
            if len(phone) <= 0:
                phone = contact_sel.xpath(
                    f'//div[contains(@class,"text-single-content")]//span[stong[contains(text(),"{location_name}")]]/..//a[contains(@href,"tel:")]//text()'
                )
            phone = "".join(phone[:1])

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store_res.text.split('"latitude":')[1]
                .split(",")[0]
                .strip('" ')
                .strip(),
                store_res.text.split('"longitude":')[1]
                .split("},")[0]
                .strip('" ')
                .strip()
                .replace('"', "")
                .strip(),
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
