# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "bluebeacon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "bluebeacon.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://bluebeacon.com/view-all-locations/"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        countries = search_sel.xpath('//div[@class="qwikpass-main"]/div')
        for country in countries:
            country_code = (
                "".join(country.xpath(".//h2/text()"))
                .strip()
                .replace("Locations", "")
                .strip()
            )
            stores = country.xpath('.//tr[./td[@data-title="Location:"]]')

            for store in stores:

                page_url = "".join(store.xpath("td/a/@href")).strip()
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                locator_domain = website

                location_name = "".join(
                    store_sel.xpath('//div[@class="sabai-directory-title"]/h1/text()')
                ).strip()

                raw_address = "".join(
                    store_sel.xpath('//div[@class="sabai-directory-location"]//text()')
                ).strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                store_number = "<MISSING>"

                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="sabai-directory-field sabai-field-type-phone sabai-field-name-field-phone sabai-clearfix"]//text()'
                    )
                ).strip()
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"

                latitude = ""
                try:
                    latitude = (
                        store_req.text.split('"lat":')[1].strip().split(",")[0].strip()
                    )
                except:
                    pass

                longitude = ""
                try:
                    longitude = (
                        store_req.text.split('"lng":')[1].strip().split(",")[0].strip()
                    )
                except:
                    pass

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
