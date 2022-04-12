from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "harleymedical.co.uk"
    start_url = "https://www.harleymedical.co.uk/our-clinics"
    scraped_urls = []

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@class="mega-menu-link" and contains(@href, "/our-clinics/")]/@href'
    )
    for store_url in all_locations:
        if store_url in scraped_urls:
            continue
        scraped_urls.append(store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//input[@name="destination"]/@value')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//section[@id="module-2"]//div[@class="col-md-6"]/p/strong/text()'
            )
        if not raw_address:
            all_locations += loc_dom.xpath(
                '//a[contains(@href, "/our-clinics/")]/@href'
            )
            continue

        location_name = loc_dom.xpath("//h1/text()")
        if not location_name:
            location_name = loc_dom.xpath('//span[@aria-current="page"]/text()')
        location_name = location_name[0]
        raw_address = raw_address[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        street_address = street_address if street_address else ""
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = loc_dom.xpath('//div[@class="clinic-details align-center"]//a/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else ""
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Opening Hours")]//following-sibling::div[1]/table//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

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
