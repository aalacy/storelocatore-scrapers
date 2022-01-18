from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzukiveiculos.com.br/concessionarias"
    domain = "suzukiveiculos.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealerships-results"]//li[address]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//a[@class="lnk-dealer"]/text()')[0]
        store_number = poi_html.xpath('.//a[contains(@href, "?id")]/@href')[0].split(
            "="
        )[-1]
        hoo = poi_html.xpath('.//strong[@class="hora-atendimento"]/following::text()')[
            0
        ]
        raw_address = poi_html.xpath(".//address/text()")[0].split(" - CEP: ")
        state = raw_address[0].split()[-1]
        page_url = f"https://www.suzukiveiculos.com.br/concessionarias/{state}/{location_name.lower().replace(' - ', ' ').replace(' ', '-')}/{store_number}"
        addr = parse_address(International_Parser(), " ".join(raw_address))
        city = addr.city
        if city and city.endswith("/"):
            city = city[:-1]
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath(".//@data-tel")[0]
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-lng")[0]
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.replace("CEP", "").strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="BR",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
