import re
from lxml import etree
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    start_url = "https://www.jimsrestaurants.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//tr[./td/a[contains(@href, "tel")]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = (
            poi_html.xpath('.//td[@headers="view-name-table-column"]/text()')
            or "<MISSING>"
        )

        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="address-line1"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@class="locality"]/text()')
        city = city[0].strip() if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="administrative-area"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@class="postal-code"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = poi_html.xpath('.//span[@class="country"]/text()')
        country_code = country_code[0].strip() if country_code else "<MISSING>"
        phone = poi_html.xpath(
            './/td[@headers="view-field-phone-table-column"]/a/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        hoo = poi_html.xpath('.//td[@headers="view-field-hours-table-column"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        row = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {zip_code}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
