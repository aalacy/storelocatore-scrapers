from lxml import etree

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("econolube_com")


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    start_url = "https://www.econolube.com/page-sitemap.xml"
    domain = "econolube.com"

    response = session.get(start_url, headers=headers)
    all_locations = []
    for line in response.iter_lines():
        line = str(line)
        if "<loc>https://www.econolube.com/locations/" in line and "-" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if (
                "0" in lurl
                or "1" in lurl
                or "2" in lurl
                or "3" in lurl
                or "4" in lurl
                or "5" in lurl
                or "6" in lurl
                or "7" in lurl
                or "8" in lurl
                or "9" in lurl
            ):
                all_locations.append(line.split("<loc>")[1].split("<")[0])

    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath('//div[@class="segment-store-info"]/h2/a/text()')
        if not location_name:
            location_name = loc_dom.xpath("//h1/text()")
        location_name = location_name[0]
        raw_address = loc_dom.xpath('//div[@class="segment-address"]/p/text()')
        if not raw_address:
            raw_address = loc_dom.xpath("//address/span/text()")
        if len(raw_address) == 1:
            raw_address += loc_dom.xpath("//address/following-sibling::span[1]/text()")
        phone = loc_dom.xpath('//div[@class="segment-address"]/div/a/text()')
        if not phone:
            phone = loc_dom.xpath('//p[@class="franchise-phone"]/a/text()')
        phone = phone[0] if phone else ""
        geo = loc_dom.xpath('//a[@title="Make this My Econo"]/@href')[0].split("/")[
            -3:-1
        ]
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Store Hours")]/following-sibling::p//text()'
        )
        hoo = hoo[:6] if hoo else ""
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[h2[contains(text(), "Store Hours:")]]/span//text()'
            )
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[-1].split(", ")[0],
            state=raw_address[-1].split(", ")[-1].split()[0],
            zip_postal=raw_address[-1].split(", ")[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
