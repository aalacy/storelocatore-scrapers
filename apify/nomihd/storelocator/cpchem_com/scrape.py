# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us

website = "cpchem.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.cpchem.com",
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
    base = "https://www.cpchem.com"
    search_url = "https://www.cpchem.com/locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_types = search_sel.xpath("//section[@class and ./h2]")

    for _type in store_types:
        store_type = (
            "Chevron Phillips Chemical " + "".join(_type.xpath("./h2/text()")).strip()
        )

        store_list = _type.xpath('.//div[contains(@class,"col")]')

        for store in store_list:

            page_url = base + "".join(store.xpath(".//h3/a/@href"))

            locator_domain = website

            location_name = "".join(store.xpath(".//h3/a/text()")).strip()
            if "Headquarters" in location_name:
                continue

            location_name = store_type
            street_address = (
                " ".join(store.xpath('.//span[@itemprop="streetAddress"]//text()'))
                .strip(",. ")
                .strip()
            )
            city = (
                "".join(store.xpath('.//span[@itemprop="addressLocality"]/text()'))
                .strip(",. ")
                .strip()
            )
            state = (
                "".join(store.xpath('.//span[@itemprop="addressRegion"]/text()'))
                .strip(",. ")
                .strip()
            )
            zip = (
                "".join(store.xpath('.//span[@itemprop="postalCode"]/text()'))
                .strip(",. ")
                .strip()
            )
            if us.states.lookup(state):
                country_code = "US"
            else:
                country_code = "<MISSING>"

            phone = "".join(store.xpath('.//*[@itemprop="telephone"]/text()')).strip()

            store_number = "<MISSING>"

            location_type = "".join(_type.xpath("./h2/text()")).strip()

            hours_of_operation = "<MISSING>"

            latitude, longitude = "<MISSING>", "<MISSING>"

            raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
