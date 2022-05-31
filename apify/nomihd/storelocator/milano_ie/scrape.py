# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "milano.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://www.milano.ie/our-restaurants/search-results", headers=headers
        )
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//a[contains(text(),"Find out more")]/@href')
        for store_url in stores:

            store_number = "<MISSING>"
            page_url = "https://www.milano.ie" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = "".join(
                store_sel.xpath('//div[@class="page-header"]/h2/text()')
            ).strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[./h4[contains(text(),"Contact Details")]]/p/text()'
                        )
                    ],
                )
            )

            raw_address = ", ".join(store_info[:-1]).strip()

            street_address = "".join(
                store_req.text.split("var address = '")[1]
                .strip()
                .split("';")[0]
                .strip()
                .replace("&#39;", "'")
            )

            state = "<MISSING>"
            zip = "".join(
                store_req.text.split("var postcode = '")[1]
                .strip()
                .split("';")[0]
                .strip()
            )

            if zip:
                city = raw_address.split(",")[-2].strip()
            else:
                city = raw_address.split(",")[-1].strip()

            if city.rsplit(" ", 1)[-1].isdigit():
                city = "".join(city.rsplit(" ", 1)[0]).strip()

            country_code = "IE"
            phone = store_info[-1]

            location_type = "<MISSING>"
            hours = store_sel.xpath(
                '//div[./h4[contains(text(),"Opening Hours")]]/ul/li'
            )

            hour_list = []
            for hour in hours:
                day = "".join(hour.xpath("strong/text()")).strip()
                time = "".join(hour.xpath("text()")).strip()
                hour_list.append(day + time)

            hours_of_operation = "; ".join(hour_list)

            latitude = (
                store_req.text.split("var restaurantLat = '")[1]
                .strip()
                .split("';")[0]
                .strip()
            )
            longitude = (
                store_req.text.split("var restaurantLng = '")[1]
                .strip()
                .split("';")[0]
                .strip()
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
