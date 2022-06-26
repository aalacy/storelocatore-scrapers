# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
import json

website = "ford.ma"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "en.fordegypt.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_urls = [
        "https://en.fordegypt.com/branchlocator",
        "https://fr.ford.ma/localisateurconcession",
    ]
    session = SgRequests()
    for search_url in search_urls:
        stores_req = session.get(search_url, headers=headers)
        log.info(search_url)
        time.sleep(5)
        search_sel = lxml.html.fromstring(stores_req.text)
        stores = search_sel.xpath("//li[@data-branch and article]")
        locator_domain = search_url.split("//")[1].split("/")[0]
        country_code = (
            locator_domain.replace("www", "")
            .replace(".", "")
            .replace("com", "")
            .replace("ford", "")
            .replace("en", "")
            .replace("fr", "")
            .strip()
            .upper()
        )
        base = "https://" + locator_domain

        for no, store in enumerate(stores, 1):

            location_type = "<MISSING>"

            page_url = base + "".join(store.xpath(".//h2/a/@href"))
            log.info(page_url)

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            store_json = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
            )
            location_name = "".join(store.xpath(".//h2/a//text()")).strip()
            if not location_name or "Service Center" in location_name:
                continue

            street_address = (
                store_json["address"]["streetAddress"]
                .replace("&#233;", "é")
                .replace("&#39;", "'")
                .strip()
            )
            city = (
                store_json["address"]["addressLocality"]
                .replace("&#233;", "é")
                .replace("&#39;", "'")
                .strip()
            )
            if city:
                city = city.split("(")[0].strip()
            state = "<MISSING>"
            zip = store_json["address"]["postalCode"]

            phone = (
                "".join(
                    store_sel.xpath(
                        '//h3[.//span[contains(text(),"Sales")]]/following-sibling::div[1]//a[contains(@href,"tel:")]//text()'
                    )
                )
                .replace("Telephone", "")
                .replace(":", "")
                .strip()
            )
            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath(
                        '//h3[.//span[contains(text(),"Ventes")]]/following-sibling::div[1]//a[contains(@href,"tel:")]//text()'
                    )
                ).strip()
                if ":" in phone:
                    phone = phone.split(":")[1].strip()

            if len(phone) <= 0:
                phone = store_sel.xpath('//span[@class="phoneNumber"]//text()')
                if len(phone) > 0:
                    phone = phone[0]
                else:
                    phone = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//h3[.//span[contains(text(),"Sales")]]/following-sibling::div[1]/div/p//text()'
                        )
                    ],
                )
            )
            if len(hours) <= 0:
                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//h3[.//span[contains(text(),"Ventes")]]/following-sibling::div[1]/div/p//text()'
                            )
                        ],
                    )
                )

            hours_of_operation = (
                "; ".join(hours)
                .strip()
                .replace(":;", ":")
                .strip()
                .replace("Vendredi;", "Vendredi:")
                .replace("Matin;", "Matin:")
                .strip()
            )

            store_number = page_url.split("/")[-1]

            latlng_info = (
                store_req.text.split("var branchMarkers =")[1]
                .split('"branchId":')[0]
                .strip()
            )

            latitude, longitude = (
                latlng_info.split('"latitude":')[1].split(",")[0].strip('" '),
                latlng_info.split('"longitude":')[1].split(",")[0].strip('" '),
            )

            if latitude == longitude:
                latitude = longitude = "<MISSING>"
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
