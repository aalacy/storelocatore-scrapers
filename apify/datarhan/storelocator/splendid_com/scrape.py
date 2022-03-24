from lxml import etree
from urllib.parse import urljoin

from sgselenium.sgselenium import SgFirefox
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "splendid.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

start_url = "https://www.splendid.com/store-locations"


def fetch_data():
    logger.info("Initiating Driver")
    with SgFirefox(user_agent=user_agent) as driver:
        driver.get(start_url)
        htmlpage = driver.page_source

        dom = etree.HTML(htmlpage)
        all_locations = dom.xpath('//div[@class="spl-store-locator__store"]')
        logger.info(f"Total Locations to crawl: {len(all_locations)}")
        for poi_html in all_locations:
            store_url = poi_html.xpath(
                './/a[@class="spl-store-locator__store__directions"]/@href'
            )[0]
            store_url = urljoin(start_url, store_url)
            logger.info(f"Crawling Page: {store_url}")

            driver.get(store_url)
            driver.implicitly_wait(30)
            html_detail_page = driver.page_source
            loc_dom = etree.HTML(html_detail_page)

            location_name = poi_html.xpath("@data-store")
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = poi_html.xpath(
                './/span[@class="spl-store-locator__store__address-line"]/text()'
            )
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            if (
                loc_dom.xpath("//address/text()")
                and "United States" in loc_dom.xpath("//address/text()")[-1]
            ):
                country_code = "US"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//li[@class="phone"]/a/text()')
            if not phone:
                phone = poi_html.xpath(
                    './/div[@class="spl-store-locator__store__tel"]/text()'
                )
            phone = phone[0].replace(".", "") if phone else "<MISSING>"
            location_type = "Store"
            latitude = loc_dom.xpath("//@data-lat")[0]
            longitude = loc_dom.xpath("//@data-long")[0]
            hoo = loc_dom.xpath(
                '//aside[@class="store-workhours"]//div[@data-role="content"]//text()'
            )
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            yield SgRecord(
                locator_domain=DOMAIN,
                store_number=store_number,
                page_url=store_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_code,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    logger.info("Crawling Started...")
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
            count = count + 1

    logger.info(f"Data Grabbing Finished and Added {count} locations")


if __name__ == "__main__":
    scrape()
