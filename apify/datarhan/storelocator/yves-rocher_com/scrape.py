import re
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

    start_url = "https://storelocator.yves-rocher.com/en/"
    domain = "yves-rocher.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath('//select[@id="country"]/option')
    for country in all_countries:
        country_id = country.xpath("@value")[0]
        country_code = country.xpath("text()")[0]
        frm = {
            "country": country_id,
            "area": "",
            "city_ft": "",
            "zip_code": "",
            "institut": "all",
            "checkinday": "",
            "checkinhour": "",
            "language": "/en/",
        }
        url = "https://storelocator.yves-rocher.com/en/search/"
        response = session.post(url, data=frm, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//span[@id="placename"]/a/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//span[@id="placename"]/text()')
            location_name = location_name[0] if location_name else ""
            raw_address = " ".join(loc_dom.xpath('//span[@id="address"]/text()'))
            if "opening soon" in raw_address.lower():
                continue
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            phone = loc_dom.xpath('//p[span[contains(text(), "Phone :")]]/text()')
            phone = phone[0] if phone else ""
            latitude = re.findall("lat = (.+?);", loc_response.text)
            latitude = latitude[0] if latitude else ""
            longitude = re.findall("lng = (.+?);", loc_response.text)
            longitude = longitude[0] if longitude else ""
            hoo = loc_dom.xpath('//div[@id="mycdbavailability"]//div//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
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
