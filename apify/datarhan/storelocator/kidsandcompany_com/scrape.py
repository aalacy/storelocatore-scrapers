from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://kidsandcompany.com/locations-across-canada/"
    domain = "kidsandcompany.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    coming_soon = dom.xpath(
        '//h2[contains(text(), "Coming Soon")]/following-sibling::div[1]//a/@href'
    )
    all_locations = dom.xpath('//div[@class="location-item"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//a/@href")[0]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_data = loc_dom.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )
        raw_address = raw_data[1:]
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        city = raw_address[1].split(", ")[0].split(" Hill - Corporate")[0]
        state = raw_address[1].split(", ")[1]
        zip_code = raw_address[1].split(", ")[-1]
        country_code = "CA"
        phone = loc_dom.xpath(
            '//h4[contains(text(), "Contact Information")]/following-sibling::p[1]/text()'
        )[0]
        location_type = ""
        if page_url in coming_soon:
            location_type = "coming soon"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else ""
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Centre Hours")]/following-sibling::p[1]/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=raw_data[0],
            street_address=raw_address[0],
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
