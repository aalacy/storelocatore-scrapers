import re
import ssl
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome, SgFirefox
from sglogging import sglog

locator_domain = "https://www.davidjones.com/"
logger = sglog.SgLogSetup().get_logger(logger_name="davidjones.com")
session = SgRequests()


def get_urls():
    r = session.get("https://www.davidjones.com/sitemaps/stores-sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def fetch_location(page_url, fox, sgw, retry=0):
    try:
        logger.info(f"Starting {page_url}")
        fox.get(page_url)
        source = fox.page_source
        logger.info(f"{page_url} got HTML")
        tree = html.fromstring(source)
        street_address = "".join(
            tree.xpath("//span[@class='store-suburb']/text()")
        ).strip()
        city = "".join(tree.xpath("//span[@class='store-city']/text()")).strip()
        state = "".join(tree.xpath("//span[@class='store-state']/text()")).strip()
        postal = "".join(tree.xpath("//span[@class='store-postcode']/text()")).strip()
        country_code = "".join(
            tree.xpath("//span[@class='store-country']/text()")
        ).strip()
        text = "".join(tree.xpath("//script[contains(text(), 'stores:')]/text()"))
        store_number = re.findall(r'id: "(.+?)"', text)[-1]
        location_name = "".join(tree.xpath("//h1/text()")).strip()
        phone = "".join(tree.xpath("//span[@class='tel-no']/text()")).strip()
        latitude = "".join(tree.xpath("//meta[@itemprop='latitude']/@content"))
        longitude = "".join(tree.xpath("//meta[@itemprop='longitude']/@content"))

        _tmp = []
        hours = tree.xpath("//div[@class='opening-hours']//tr")
        for h in hours:
            day = "".join(h.xpath("./td[1]//text()")).strip()
            inter = "".join(h.xpath("./td[2]//text()")).strip()

            if day.endswith("th"):
                continue

            _tmp.append(f"{day}: {inter}")

        hours_of_operation = re.sub("\n", "", ";".join(_tmp))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)

    except:
        return fetch_location(page_url, fox, sgw, retry + 1)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"{len(urls)} URLs need to crawl...")

    with SgFirefox(is_headless=True) as fox:
        for page_url in urls:
            fetch_location(page_url, fox, sgw)


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
