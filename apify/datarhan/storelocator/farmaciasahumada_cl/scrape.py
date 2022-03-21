from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.farmaciasahumada.cl/storelocator"
    domain = "farmaciasahumada.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="stores"]/li')
    next_page = dom.xpath('//a[@class="action  next"]/@href')
    while next_page:
        response = session.get(next_page[0])
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//ul[@class="stores"]/li')
        next_page = dom.xpath('//a[@class="action  next"]/@href')

    for poi_html in all_locations:
        street_address = poi_html.xpath(".//strong/text()")[0]
        city = (
            poi_html.xpath(".//p[1]//text()")[0]
            .strip()
            .replace("Región del", "")
            .replace("Región de", "")
            .replace("Región", "")
        )
        hoo = poi_html.xpath('.//p[@class="store-schedule"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="",
            store_number="",
            phone="",
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
