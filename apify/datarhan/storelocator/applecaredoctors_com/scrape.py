from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_usa
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://applecareurgentcare.com/urgent-care-locations/"
    domain = "applecareurgentcare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@title="VIEW DETAILS"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")
        if location_name:
            location_name = location_name[-1]
            raw_address = loc_dom.xpath(
                '//h3[img[contains(@src, "address")]]/following-sibling::p[@class="clinic-detail-item"]/text()'
            )
            raw_address = ", ".join([e.strip() for e in raw_address]).replace(
                "\n", ", "
            )
            addr = parse_address_usa(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            country_code = addr.country
            phone = loc_dom.xpath(
                '//p[@class="single-clinic-phone-number clinic-detail-item"]/a/text()'
            )[0]
            hoo = loc_dom.xpath('//div[@class="todays-hours"]//p/text()')
            hoo = " ".join(hoo).split("We are")[0]
            geo = (
                loc_dom.xpath("//iframe/@src")[-1]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            latitude = geo[1]
            longitude = geo[0]
        else:
            location_name = loc_dom.xpath("//h3/text()")[0]
            raw_address = loc_dom.xpath(
                '//h3[contains(text(), "Address")]/following-sibling::h3/text()'
            )[0].split(", ")
            street_address = " ".join(raw_address[0].split())
            city = raw_address[1]
            state = raw_address[2].split()[0]
            zip_code = raw_address[2].split()[-1]
            country_code = ""
            phone = loc_dom.xpath('//h3[contains(text(), "Ph.:")]/text()')
            phone = phone[0].split(": ")[-1] if phone else ""
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Hours")]/following-sibling::div//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            latitude = ""
            longitude = ""
            raw_address = ""

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
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
