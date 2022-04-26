import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "granitetransformations.co.uk"
    start_url = "https://www.granitetransformations.co.uk/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//h2[contains(text(), "All Showrooms")]/following-sibling::ul//h4/a/@href'
    )
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//h1[contains(text(), "Showroom Closed")]'):
            continue
        raw_address = loc_dom.xpath(
            '//p[strong[contains(text(), "Postal Address")]]/text()'
        )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//a[@class="franchise_tile col-md-4"]/span[@class="excerpt"]/text()'
            )
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()]).split(
            "See what"
        )[0]
        addr = parse_address_intl(raw_address)
        location_name = store_url.split("/")[-1].capitalize()
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = "{} {}".format(
                addr.street_address_2, addr.street_address_1
            )
        if street_address and "We Are Currently Running" in street_address:
            street_address = ""
        if "a mobile showroom" in raw_address:
            raw_address = ""
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if street_address and "Ph1 5Js" in street_address:
            zip_code = "PH1 5JS"
            street_address = street_address.replace(" Ph1 5Js", "")
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else ""
        geo = loc_dom.xpath('//img[contains(@data-src, "map")]/@data-src')
        latitude = ""
        longitude = ""
        if geo:
            geo = geo[0].split("map-")[-1].split("-")[:3]
            latitude = geo[0]
            longitude = geo[1]
        if not geo:
            geo = re.findall(r"maps.LatLng\((.+?)\)", loc_response.text)
            if geo:
                geo = geo[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
        hoo = loc_dom.xpath('//div[@class="franchise_tile col-md-4"]//table//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="UK",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
