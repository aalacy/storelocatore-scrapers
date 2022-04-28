from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import sglog
from sgselenium import SgChrome
import ssl


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_urls():
    with SgChrome() as driver:
        driver.get("https://www.office.co.uk/view/content/storelocator")
        tree = html.fromstring(driver.page_source, "lxml")

    return tree.xpath("//div[contains(@id, 'addressDetail')]/a/@href")


def fetch_data():
    urls = get_urls()
    log.info(f"Total URLs to crawl: {len(urls)}")
    with SgChrome() as driver:
        for slug in urls:
            page_url = f"https://www.office.co.uk/view/content/storelocator{slug}"
            driver.get(page_url)
            tree = html.fromstring(driver.page_source, "lxml")

            line = tree.xpath(
                "//ul[@class='storelocator_addressdetails_address darkergrey']/li/text()"
            )
            line = list(filter(None, [li.strip() for li in line]))
            if line:
                location_name = line.pop(0)
            else:
                location_name = SgRecord.MISSING

            raw_address = ", ".join(line)
            phone = "".join(
                tree.xpath(
                    "//div[@class='storelocator_contactdetails floatProperties']/div[1]/text()"
                )
            ).strip()

            street_address, city, postal = get_international(raw_address)
            country_code = "GB"
            if " " not in postal and postal != SgRecord.MISSING:
                country_code = "DE"

            text = "".join(tree.xpath("//script[contains(text(),'LatLng')]/text()"))
            try:
                latitude, longitude = eval(text.split("LatLng")[1].split(");")[0])
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            _tmp = []
            hours = tree.xpath(
                "//ul[@class='storelocator_open_times_content']/li//text()"
            )
            hours = list(filter(None, [h.strip() for h in hours]))
            for h in hours:
                if h.endswith("-"):
                    continue
                _tmp.append(h)

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            yield row


if __name__ == "__main__":
    locator_domain = "https://www.office.co.uk/"
    ssl._create_default_https_context = ssl._create_unverified_context
    log = sglog.SgLogSetup().get_logger(logger_name="office.co.uk")

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
