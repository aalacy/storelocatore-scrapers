# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "darlington.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.darlington.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.darlington.co.uk/branches/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = stores_req.text.split("stores.push(")
        for index in range(1, len(stores)):
            store_info = stores[index].split(");")[0].strip()
            page_url = (
                store_info.split("link:")[1]
                .strip()
                .split("}")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = (
                store_info.split("name:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            street_address = (
                store_info.split("address1:")[1]
                .strip()
                .split("',")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            if "," in street_address:
                street_address = street_address.split(",")[-1].strip()
            city = (
                store_info.split("address2:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
                .strip()
            )

            state = "<MISSING>"
            zip = (
                store_info.split("address3:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            country_code = "GB"
            phone = (
                "".join(
                    store_sel.xpath(
                        '//div[@class="store__details__contacts"]/p/a[contains(@href,"tel:")]/text()'
                    )
                )
                .strip()
                .replace("T:", "")
                .strip()
            )

            location_type = "<MISSING>"
            store_number = (
                store_info.split("post_id:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            hours = store_sel.xpath('//div[@class="store__details__hours__all"]/div')
            hours_list = []
            for hour in hours:
                day = "".join(
                    hour.xpath("div[@class='store__details__hours__name']/text()")
                ).strip()
                time = "".join(
                    hour.xpath("div[@class='store__details__hours__times']/text()")
                ).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = (
                store_info.split("lat:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
                .strip()
            )
            longitude = (
                store_info.split("lng:")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("'", "")
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
