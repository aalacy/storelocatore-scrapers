# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jackwilliams.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "jackwilliams.com",
    "accept": "*/*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://jackwilliams.com",
    "referer": "https://jackwilliams.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "x-newrelic-id": "VgEBU1FSCBAFU1NbBQICX1U=",
    "x-requested-with": "XMLHttpRequest",
}

data = {
    "currentUrl": "https://jackwilliams.com/",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_res = session.post(
            "https://jackwilliams.com/default/iwd_sa/ajax/addressSearch",
            headers=headers,
            data=data,
        )
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="amlocator-store-information"]')[1:]

        for store in stores:

            page_url = "".join(store.xpath(".//a[1]/@href")[0]).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(store.xpath(".//a[1]/text()")).strip()

            street_address = "".join(
                store_sel.xpath(
                    '//div[@class="store-address"]/span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@class="store-address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//div[@class="store-address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@class="store-address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()
            store_number = "<MISSING>"
            country_code = "US"

            phone = "".join(
                store_sel.xpath('//div[@class="location-phone-container"]//text()')
            ).strip()

            location_type = "<MISSING>"
            hours_of_operation = "; ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@class="store-hours"]/div[1]/text()'
                            )
                        ],
                    )
                )
            ).strip()
            latitude, longitude = (
                store_req.text.split("Lat:")[1].strip().split(",")[0].strip(),
                store_req.text.split("Lng:")[1].strip().split(",")[0].strip(),
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
