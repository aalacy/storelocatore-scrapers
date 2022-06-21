from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.mcdonalds.it/elenco-ristoranti"
    domain = "mcdonalds.it"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="store-list--content"]//a/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/span/text()")
        if not location_name:
            continue
        location_name = location_name[0]
        raw_address = loc_dom.xpath('//div[@class="store__address"]/text()')
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
        hoo = loc_dom.xpath('//div[@class="hours__list"]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split("Tutti")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state="",
            zip_postal="",
            country_code="IT",
            store_number="",
            phone=raw_address[2].split(":")[1],
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
