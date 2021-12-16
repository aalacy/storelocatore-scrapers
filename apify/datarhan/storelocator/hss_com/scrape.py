import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "hss.com"
    start_url = "https://www.hss.com/hire/find-a-branch/all-branches"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//select[@class="chosen-select customSelect"]/option/@value'
    )
    for url in list(set(all_locations)):
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//div[@itemprop="address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address) == 5:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        poi_name = re.findall('storename="(.+?)";', loc_response.text)
        if not poi_name:
            continue
        poi_name = poi_name[0]
        street = raw_address[0]
        street = street.split('";var')[0].strip()
        city = raw_address[1]
        zip_code = re.findall('storeaddresspostalCode="(.+?)";', loc_response.text)
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = re.findall('storeaddresscountryname="(.+?)";', loc_response.text)
        country_code = country_code[0] if country_code else "<MISSING>"
        phone = re.findall('storeaddressphone="(.+?)";', loc_response.text)
        phone = phone[0] if phone else "<MISSING>"
        latitude = re.findall("latitude=(.+?);", loc_response.text)[0]
        longitude = re.findall("longitude=(.+?);", loc_response.text)[0]
        hoo = loc_dom.xpath('//div[@class="store-openings weekday_openings"]//text()')
        hoo = [
            elem.strip().replace("\t", "").replace("\n", " ")
            for elem in hoo
            if elem.strip()
        ]
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=poi_url,
            location_name=poi_name,
            street_address=street,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
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
