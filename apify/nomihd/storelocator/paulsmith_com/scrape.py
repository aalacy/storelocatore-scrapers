# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "paulsmith.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    # Your scraper here

    search_url = "https://www.paulsmith.com/uk/shop-locator"
    log.info(f"Crawling {search_url}")
    driver = get_driver(search_url)
    search_sel = lxml.html.fromstring(driver.page_source)
    countries = search_sel.xpath('//select[@id="country-shops"]/option/@value')
    for country in countries:
        log.info(f"fetching stores for country:{country}")

        driver.get(f"https://www.paulsmith.com/uk/shop-locator/{country}")
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath(
            '//li[@class="card pl-0"]/a[@class="card-image-wrapper"]/@href'
        )
        for store_url in stores:

            locator_domain = website
            page_url = store_url
            log.info(page_url)
            driver = get_driver(page_url)
            store_sel = lxml.html.fromstring(driver.page_source)
            temp_city = "".join(
                store_sel.xpath('//span[@class="text-block-badge"]/text()')
            ).strip()

            location_name = "".join(
                store_sel.xpath('//h1[@class="text-block-heading"]/text()')
            ).strip()
            location_type = "<MISSING>"

            raw_address = ", ".join(
                store_sel.xpath('//address[@class="mb-0"]/p/text()')
            ).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = temp_city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = country

            phone = (
                "".join(store_sel.xpath('//address//a[contains(@href,"tel:")]/text()'))
                .strip()
                .replace("Tel:", "")
                .strip()
            )

            hours = store_sel.xpath(
                '//div[./h2[contains(text(),"Opening Hours")]]//li[@class="info-block-list-item"]'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("text()")).strip()
                time = "".join(hour.xpath("span/text()")).strip()
                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if hours_of_operation:
                if hours_of_operation.count("Closed") == 7:
                    location_type = "Closed"

            store_number = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//a[contains(text(),"Get Directions")]/@href')
            ).strip()

            latitude, longitude = "<MISSING>", "<MISSING>"

            if "/dir/" in map_link:
                latlng = map_link.split("/dir/")[1].strip().split("?")[0].strip()
                latitude = latlng.split(",")[0].strip()
                longitude = latlng.split(",")[1].strip()

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
