# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sarkujapan.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.sarkujapan.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sarkujapan.com/locations/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = stores_req.text.split("var marker")
        for index in range(2, len(stores) - 1):
            store_info = stores[index].split("});")[0].strip()
            store_sel = lxml.html.fromstring(
                store_info.split(".bindPopup('")[1].strip().split("');")[0].strip()
            )

            raw_info = store_sel.xpath(
                '//div[@class="wpb_text_column wpb_content_element "]'
            )
            location_name = raw_info[1].xpath(".//p//text()")[0].strip()
            page_url = search_url
            locator_domain = website

            raw_address = raw_info[1].xpath(".//p//text()")[1:]
            street_address = ", ".join(raw_address[:-1]).strip()
            city = "".join(raw_address[-1]).strip().split(",")[0].strip()
            state = (
                "".join(raw_address[-1])
                .strip()
                .split(",")[-1]
                .strip()
                .split(" ")[0]
                .strip()
            )
            zip = (
                "".join(raw_address[-1])
                .strip()
                .split(",")[-1]
                .strip()
                .split(" ")[-1]
                .strip()
            )

            phone = "".join(
                raw_info[2].xpath('.//a[contains(@href,"tel:")]/text()')
            ).strip()
            hours_of_operation = (
                "; ".join(raw_info[2].xpath(".//p/text()"))
                .strip()
                .replace("Phone: ;", "")
                .strip()
                .replace("Hours:", "")
                .strip()
            )

            country_code = "US"

            store_number = "".join(store_info.split("=")[0]).strip()

            location_type = " ".join(raw_info[0].xpath(".//p//text()"))

            latitude = (
                "".join(store_info)
                .split("L.marker([")[1]
                .strip()
                .split(",")[0]
                .strip()
                .split("]")[0]
                .strip()
            )
            longitude = (
                "".join(store_info)
                .split("L.marker([")[1]
                .strip()
                .split(",")[1]
                .strip()
                .split("]")[0]
                .strip()
                .split("{")[0]
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
