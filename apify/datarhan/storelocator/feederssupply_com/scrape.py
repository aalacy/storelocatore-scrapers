from lxml import etree
from time import sleep

from sgselenium import SgChrome
from selenium.webdriver.common.by import By

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sglogging import sglog
import ssl

domain = "feederssupply.com"

ssl._create_default_https_context = ssl._create_unverified_context

logger = sglog.SgLogSetup().get_logger(logger_name=domain)


def fetch_data():

    start_url = "https://www.feederssupply.com/store-locator"

    with SgChrome() as driver:

        driver.get(start_url)
        try:
            driver.find_element(By.XPATH, '//div[@aria-label="Back to site"]').click()
        except Exception:
            pass

        all_locations_urls = driver.find_elements_by_xpath(
            '//a[@data-testid="linkElement" and span[contains(text(), "Location Page")]]'
        )
        for i, url in enumerate(all_locations_urls):
            poi = all_locations_urls[i]
            poi.location_once_scrolled_into_view
            try:
                driver.execute_script("window.scrollBy(0, -400);")
                driver.execute_script("arguments[0].click();", poi)
            except Exception:
                driver.execute_script("window.scrollBy(0, -200);")
                driver.execute_script("arguments[0].click();", poi)
            sleep(30)
            poi_html = etree.HTML(driver.page_source)
            raw_data = poi_html.xpath(
                '//div[p[span[span[span[span[@style="font-family:futura-lt-w01-book,sans-serif"]]]]]]/p//text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip() and len(e) > 1]
            store_url = start_url
            location_name = raw_data[0]
            location_name = location_name if location_name else "<MISSING>"
            logger.info(f"Location Name: {location_name}")
            street_address = raw_data[1]
            city = raw_data[2].split(", ")[0]
            state = raw_data[2].split(", ")[-1].split()[0]
            zip_code = raw_data[2].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = raw_data[3]
            location_type = "<MISSING>"
            hoo = poi_html.xpath(
                '//p[span[span[span[span[contains(text(),"Store Hours")]]]]]/following-sibling::p[1]//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            iframe = driver.find_element_by_xpath('//iframe[@title="Google Maps"]')
            driver.switch_to.frame(iframe)
            poi_html = etree.HTML(driver.page_source)
            driver.switch_to.default_content()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            geo = poi_html.xpath('//a[contains(@href, "maps")]/@href')
            if geo:
                geo = geo[-1].split("/@")[-1].split(",")[:2]
                if len(geo) == 2:
                    latitude = geo[0]
                    longitude = geo[1]
            if "http" in latitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            driver.find_element(
                By.XPATH, '//div[@data-testid="popupCloseIconButtonRoot"]'
            ).click()

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    logger.info(f"Crawling Started...")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)
            count = count + 1

    logger.info(f"Total Locations: {count}")


if __name__ == "__main__":
    scrape()
