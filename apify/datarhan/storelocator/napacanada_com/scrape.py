import ssl
import json
from lxml import etree
from urllib.parse import urljoin

from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def get(url, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        fetch("{url}")
            .then(res => res.text())
            .then(done)
    """
    )


def extract_details(html):
    loc_dom = etree.HTML(html)
    scripts = loc_dom.xpath('//script[@type="application/ld+json"]/text()')

    for script in scripts:
        if "address" in script:
            return json.loads(script)


def fetch_data():
    # Your scraper here
    domain = "napacanada.com"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

    with SgChrome(user_agent=user_agent).driver() as driver:
        driver.get("https://www.napacanada.com/")
        driver.implicitly_wait(20)
        start_url = "https://www.napacanada.com/en/store-finder?q=H1N+3E2&page=7"
        html = get(start_url, driver)
        dom = etree.HTML(html)

        all_locations = dom.xpath('//li[@class="aadata-store-item"]')
        for poi_html in all_locations:
            store_url = poi_html.xpath('.//a[@class="storeWebsiteLink"]/@href')[0]
            store_url = urljoin(start_url, store_url)
            html = get(store_url, driver)
            poi = extract_details(html)
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            hoo = []
            for elem in poi["openingHoursSpecification"]:
                day = elem["dayOfWeek"][0]
                opens = elem["opens"]
                closes = elem["closes"]
                hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=poi["name"],
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["addressCountry"],
                store_number=poi["@id"],
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
