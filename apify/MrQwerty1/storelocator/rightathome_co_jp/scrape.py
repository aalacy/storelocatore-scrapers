from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgpostal import parse_address, International_Parser
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
        is_headless=True,
    ).driver() as driver:
        driver.get(page_url)

        tree = html.fromstring(driver.page_source)
    divs = tree.xpath("//div[@class='contents_box' and .//table]")

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::h4/text()")).strip()
        raw_address = " ".join(
            " ".join(
                d.xpath(".//th[contains(text(), '所在地')]/following-sibling::td//text()")
            ).split()
        )
        street_address, city, state, postal = get_international(raw_address)
        country_code = "JP"
        phone = (
            "".join(
                d.xpath(".//th[contains(text(), 'TEL')]/following-sibling::td/text()")
            )
            .split("FAX")[0]
            .replace("TEL", "")
            .strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    os.environ[
        "PROXY_URL"
    ] = "http://groups-RESIDENTIAL,country-jp:{}@proxy.apify.com:8000/"
    locator_domain = "http://www.rightathome.co.jp/"
    page_url = "http://www.rightathome.co.jp/company.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
