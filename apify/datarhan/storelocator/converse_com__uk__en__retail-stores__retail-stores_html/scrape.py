from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.converse.com/uk/en/retail-stores/retail-stores.html"
    domain = "onverse.com/uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//li[@class="content-page"]/div/p[b[contains(text(), "Converse")]]'
    )
    for poi_html in all_locations:
        location_name = "Converse Brand Outlet Store"
        raw_adr = poi_html.xpath("text()")[3:]
        raw_adr = [e.strip() for e in raw_adr]
        addr = parse_address_intl(" ".join(raw_adr))
        country_code = addr.country
        country_code = poi_html.xpath(".//preceding-sibling::h2[1]/b/text()")[0]
        latitude = ""
        longitude = ""
        geo = poi_html.xpath('.//a[contains(@href, "/@")]/@href')
        if geo:
            geo = geo[0].split("@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        city = addr.city
        street_address = raw_adr[0]
        if not city and street_address == "Via della Pace":
            city = "Valmontone"
            street_address += " " + "- Unit 74"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=addr.postcode,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
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
