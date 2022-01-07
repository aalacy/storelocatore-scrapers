# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "absolutedental.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.absolutedental.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        regions_req = session.get(
            "https://www.absolutedental.com/locations/", headers=headers
        )
        regions_sel = lxml.html.fromstring(regions_req.text)
        regions = regions_sel.xpath('//div[@class="location-city-box"]/a/@href')
        for region_url in regions:
            stores_req = session.get(region_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//a[contains(text(),"View Location Details")]/@href'
            )
            for store_url in stores:
                page_url = store_url
                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                locator_domain = website
                location_name = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]/div[@class="location-address"]/h3/text()'
                    )
                ).strip()

                store_number = "<MISSING>"

                location_type = "<MISSING>"

                raw_info = store_sel.xpath(
                    '//div[@class="location-info"]/div[@class="location-address"]/p/text()'
                )
                street_address = ", ".join(raw_info[:-2]).strip()
                city = raw_info[-2].strip().split(",")[0].strip()
                state = (
                    raw_info[-2]
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .replace("\t\t\t\t\t", " ")
                    .strip()
                    .rsplit(" ", 1)[0]
                    .strip()
                )
                zip = (
                    raw_info[-2]
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .replace("\t\t\t\t\t", " ")
                    .strip()
                    .rsplit(" ")[-1]
                    .strip()
                )

                country_code = "US"

                phone = raw_info[-1].strip().replace("Phone Number:", "").strip()

                hours = store_sel.xpath('//div[@class="location-hours"]/p/text()')
                hours_list = []
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

                hours_of_operation = "; ".join(hours_list).strip()

                latitude, longitude = (
                    store_res.text.split('"lat":"')[1].strip().split('",')[0].strip(),
                    store_res.text.split('"lng":"')[1].strip().split('"}')[0].strip(),
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
