# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from sgselenium import SgChrome
from selenium.webdriver.chrome.options import Options

website = "canadagoose.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = (
        "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
    )

    chrome_options = Options()
    chrome_options.accept_untrusted_certs = True
    chrome_options.assume_untrusted_cert_issuer = True
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--allow-http-screen-capture")
    chrome_options.add_argument("--disable-impl-side-painting")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-seccomp-filter-sandbox")

    with SgChrome(
        is_headless=True,
        chrome_options=chrome_options,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    ) as session:
        session.get(search_url)
        log.info(session.page_source)
        search_sel = lxml.html.fromstring(session.page_source, "lxml")
        store_list = search_sel.xpath('//div[@class="store"]')
        log.info(f"Total Locations to crawl: {len(store_list)}")
        for store in store_list:

            page_url = store.xpath("./a/@href")[0].strip()
            log.info(f"Now crawling: {page_url}")
            session.get(page_url)
            time.sleep(3)
            store_sel = lxml.html.fromstring(session.page_source, "lxml")

            locator_domain = website

            street_address = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="streetAddress"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            city = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="addressLocality"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            try:
                if city[-1] == ",":
                    city = "".join(city[:-1]).strip()
            except:
                city = "<MISSING>"

            state = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="addressRegion"]//text()'
                )
            ).strip()
            zip = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="postalCode"]//text()'
                )
            ).strip()

            if len(street_address) <= 0:
                street_address = ", ".join(
                    "".join(
                        store_sel.xpath(
                            '//div[@class="store-info desktop"]//*[@itemprop="address"]//text()'
                        )
                    )
                    .strip()
                    .split(",")[:-1]
                ).strip()

            country_code = "<INACCESSIBLE>"
            if "Italy" == state:
                country_code = "IT"
                state = "<MISSING>"
            if "France" == state:
                country_code = "FR"
                state = "<MISSING>"
            if "Taiwan" == state:
                country_code = "TW"
                state = "<MISSING>"

            try:
                if state.split(" ")[0].strip().isdigit():
                    zip = state.split(" ", 1)[0].strip()
                    state = state.split(" ", 1)[-1].strip()
            except:
                pass
            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//span[@itemprop="name"]/text()'
                )
            ).strip()

            phone = store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="telephone"]//text()'
            )
            if len(phone) > 0:
                phone = "".join(phone[0]).strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours = store_sel.xpath('//div[@class="store-info desktop"]/text()')
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            if len(hours_list) <= 0:
                hours = store_sel.xpath(
                    '//div[@class="store-info desktop"]/p[./meta[@itemprop="openingHours"]]/text()'
                )
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

            if len(hours_list) <= 0:
                hours = store_sel.xpath('//div[@class="store-info desktop"]/p/text()')
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

            hours_of_operation = "; ".join(hours_list).strip()
            if "," == hours_of_operation:
                hours_of_operation = "<MISSING>"

            map_link = "".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//a[contains(@href,"maps")]/@href'
                )
            )

            latitude, longitude = get_latlng(map_link)

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
