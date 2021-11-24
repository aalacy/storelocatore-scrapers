import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://kaspas.co.uk/our-locations/"
    domain = "kaspas.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li/a[contains(@href, "/location/")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//p[contains(text(), "Coming Soon")]'):
            continue
        location_name = loc_dom.xpath("//h1/text()")[0]
        country_code = ""
        if location_name == "Pakistan":
            country_code = "Pakistan"
        raw_address = loc_dom.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::p/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip() and "Email" not in e]
        if not raw_address:
            continue
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = addr.postcode
        if not zip_code:
            zip_code = " ".join(raw_address).split(", ")[-1]
        street_address = street_address.replace("Wd24 5Bq", "").strip()
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].strip() if phone else ""
        geo = re.findall(r"maps.LatLng\((.+?)\);", loc_response.text)[0].split(", ")
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Open Hours")]/following-sibling::ul//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("Open for")[0].strip()
        if hoo == "Temporarily Closed":
            continue
        city = addr.city
        if not city:
            city = raw_address[-2].strip()
        if city.endswith(","):
            city = city[:-1]
        if city == "6 -8 0SMOSTON ROAD":
            city = location_name
        city = city.replace("Super Market", "").split("Postal")[0].strip()
        if zip_code in ["St Helens.", "Cwmbran"]:
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=" ".join(raw_address),
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
