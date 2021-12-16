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

    start_url = "https://www.sals-pizza.com/"
    domain = "sals-pizza.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[div[div[div[p[contains(text(), "LOCATIONS")]]]]]/following-sibling::ul/li/a/@href'
    )
    for store_url in all_locations:
        if "coming-soon" in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath(
            "//div[h1]/following-sibling::div[1]/h2/span//text()"
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]//text()')
        phone = phone[0] if phone else SgRecord.MISSING
        hoo = loc_dom.xpath(
            '//div[h1[span[span[contains(text(), "Hours")]]]]/following-sibling::div[@data-testid="richTextElement"][1]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("*")[0].strip()
        if "Store hours" in hoo:
            hoo = SgRecord.MISSING
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        if len(zip_code.strip()) == 2:
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=loc_dom.xpath("//div/h1/span/span/text()")[0],
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
