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

        raw_address = loc_dom.xpath(
            '//a[@class="franchise_tile col-md-4"]/span[@class="excerpt"]/text()'
        )[0].strip()
        addr = parse_address_intl(raw_address)
        location_name = store_url.split("/")[-1].capitalize()
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = "{} {}".format(
                addr.street_address_2, addr.street_address_1
            )
        if "We Are Currently Running" in street_address:
            street_address = ""
        if "a mobile showroom" in raw_address:
            raw_address = ""
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if "Ph1 5Js" in street_address:
            zip_code = "PH1 5JS"
            street_address = street_address.replace(" Ph1 5Js", "")
        country_code = addr.country
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else ""
        geo = (
            loc_dom.xpath('//img[contains(@data-src, "map")]/@data-src')[0]
            .split("map-")[-1]
            .split("-")[:3]
        )
        if geo[-1] == "385":
            geo = geo[:-1]
        latitude = geo[0]
        longitude = geo[-1]
        hoo = loc_dom.xpath('//div[@class="franchise_tile col-md-4"]//table//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""
        if "Monday Appointment Only" in hours_of_operation:
            hours_of_operation = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
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
