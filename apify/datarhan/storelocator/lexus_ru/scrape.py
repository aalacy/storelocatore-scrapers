from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://serviceportal.lexus.ru/static/dealer-locator"
    domain = "lexus.ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text.replace("\\", ""))

    all_locations = dom.xpath('//div[@class="locator__dealer"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//@data-dealer-name")[0]
        raw_address = poi_html.xpath(
            './/div[@class="locator__dealer__address"]/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        store_number = poi_html.xpath("@data-center-id")[0]
        geo = (
            poi_html.xpath('.//div[@class="locator__dealer__route"]/a/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        city = addr.city
        if city:
            city = city.replace("Г.", "").strip()
        if city == "П.":
            city = "Солнечный"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://serviceportal.lexus.ru/static/dealer-locator",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="RU",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation="",
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
