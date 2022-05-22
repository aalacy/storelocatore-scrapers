# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "tazauae.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.tazauae.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.tazauae.com/taza-stores/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        hoo_req = session.get("https://www.tazauae.com/", headers=headers)
        hoo_sel = lxml.html.fromstring(hoo_req.text)
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        cities = stores_sel.xpath(
            '//li[contains(@id,"menu-item-")][.//div[@class="tcb-mega-drop"]]'
        )
        for cit in cities:
            stores = cit.xpath(".//ul/li/a/@href")
            for store_url in stores:
                page_url = store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                locator_domain = website
                raw_info = store_sel.xpath(
                    '//div[@class="thrv_wrapper thrv_text_element"]'
                )
                location_name = "".join(raw_info[0].xpath("p/strong/text()")).strip()

                raw_address = "".join(raw_info[1].xpath("p/text()")).strip()
                street_address = raw_address
                state = "<MISSING>"
                zip = "<MISSING>"

                city = "".join(cit.xpath("a/span/text()")).strip()

                street_address = (
                    street_address.strip()
                    .split("UAE")[0]
                    .strip()
                    .replace(". MAP", "")
                    .strip()
                )
                if (
                    city.title()
                    == street_address.split(",")[-1].strip().replace(".", "").strip()
                ):
                    street_address = ", ".join(street_address.split(",")[:-1]).strip()
                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = "UAE"
                store_number = "<MISSING>"

                phone = (
                    "".join(
                        store_sel.xpath(
                            '//a[./img[contains(@src,"phone01.png")]]/@href'
                        )
                    )
                    .strip()
                    .replace("tel:", "")
                    .strip()
                )

                location_type = "<MISSING>"

                hours_of_operation = (
                    "".join(
                        hoo_sel.xpath(
                            '//div[@class="thrv_wrapper thrv_text_element"]/p[./strong/span[contains(text(),"Restaurant")]]/strong/span/text()'
                        )
                    )
                    .strip()
                    .split("Restaurant")[-1]
                    .strip()
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"
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
