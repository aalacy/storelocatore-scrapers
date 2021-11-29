# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import ssl
from lxml import etree

from sgrequests import SgRequests
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


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.co.il/dealers/dealers"
    domain = "toyota.co.il"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="fullwidth-element paragraph-side col-xs-12 col-sm-6 col-md-3" and section]'
    )
    for poi_html in all_locations:
        city = poi_html.xpath(".//*/strong/text()")[0]
        location_name = poi_html.xpath(".//div/strong/text()")[0]
        street_address = poi_html.xpath('.//a[contains(@href, "waze")]/text()')[0]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        hoo = poi_html.xpath(
            './/div[strong[contains(text(), "שעות פתיחה אולם תצוגה")]]/following-sibling::div//text()'
        )
        if not hoo:
            hoo = poi_html.xpath(
                './/div[strong[span[contains(text(), "שעות פתיחה אולם תצוגה")]]]/following-sibling::div//text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("שעות")[0].strip()
        if not hoo:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://toyota.co.il/#/box-ajax/url=%2Fdealers%2Fdealers/size=fullscreen",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="IL",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
