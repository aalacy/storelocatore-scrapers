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

    start_url = "https://www.bathstore.com/stores"
    domain = "bathstore.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//li[@class="storesList_locations"]/a/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath(
            '//h3[@class="storeDetailMap_locationName_title"]/text()'
        )
        if not location_name:
            continue
        location_name = location_name[0]
        raw_address = loc_dom.xpath('//div[@class="storeDetailMap_address"]/p/text()')
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += " " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        phone = loc_dom.xpath(
            '//div[@class="storeDetailMap_locationInformation"]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else ""
        geo = loc_dom.xpath("//@data-latlong")[0].split(",")
        hoo = loc_dom.xpath(
            '//li[@class="storeDetailMap_openingTime_item"]/span/text()'
        )
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
