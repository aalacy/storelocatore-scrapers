import ssl
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgFirefox
from urllib.parse import unquote
from sglogging import SgLogSetup
from selenium import Driver
from selenium_stealth import stealth

logger = SgLogSetup().get_logger("bluenile.com")


def get_urls(driver):
    driver.get("https://www.bluenile.com/jewelry-stores")
    driver.execute_script("open('https://www.bluenile.com/jewelry-stores')")
    time.sleep(120)
    driver.refresh()
    source = driver.page_source
    logger.info(source)
    tree = html.fromstring(source)
    return tree.xpath("//a[@class='store-name']/@href")


def fetch_data(sgw: SgWriter):
    with SgFirefox(user_agent=user_agent, is_headless=True) as driver:
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        urls = get_urls(driver)
        for page_url in urls:
            driver.get(page_url)
            time.sleep(60)
            source = driver.page_source
            tree = html.fromstring(source)

            location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
            street_address = "".join(
                tree.xpath("//span[@itemprop='streetAddress']/text()")
            ).strip()
            city = "".join(
                tree.xpath("//span[@itemprop='addressLocality']/text()")
            ).strip()
            state = "".join(
                tree.xpath("//span[@itemprop='addressRegion']/text()")
            ).strip()
            postal = "".join(
                tree.xpath("//span[@itemprop='postalCode']/text()")
            ).strip()
            phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()

            try:
                text = unquote(
                    "".join(tree.xpath("//a[contains(text(), 'View On Map')]/@href"))
                )
                latitude, longitude = text.split("/@")[1].split(",")[:2]
            except IndexError:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            _tmp = []
            hours = tree.xpath("//dl/dt")
            for h in hours:
                day = "".join(h.xpath("./span[1]/text()")).strip()
                inter = "".join(
                    h.xpath("./following-sibling::dd[1]/time/text()")
                ).strip()
                _tmp.append(f"{day} {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bluenile.com/"
    ssl._create_default_https_context = ssl._create_unverified_context
    user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firedriver/78.0"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
