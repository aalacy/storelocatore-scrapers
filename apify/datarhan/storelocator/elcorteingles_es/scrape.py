import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.elcorteingles.es/centroscomerciales/es/eci"
    domain = "elcorteingles.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="home-centers-list"]//a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="text-center"]/text()')[0]
        raw_address = loc_dom.xpath(
            '//dt[i[@class="fa fa-map-marker"]]/following-sibling::dd[1]/text()'
        )
        street_address = ""
        city = ""
        zip_code = ""
        country = ""
        if raw_address:
            raw_address = raw_address[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.split()[0]
            country = addr.country
        phone = loc_dom.xpath('//a[@class="phone"]/text()')[0].strip()
        geo = json.loads(loc_dom.xpath("//@data-location")[0])
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Calendario de apertura")]/following-sibling::ul//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo[:2])
        if not raw_address:
            raw_address = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country,
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo["lat"],
            longitude=geo["lng"],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
