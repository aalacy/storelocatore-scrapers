from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.sephora.com.br/nossas-lojas/"
    domain = "sephora.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@id="stores"]/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h4/text()")[0]
        zip_code = poi_html.xpath("@data-zip")[0].split(", ")[0]
        city = poi_html.xpath("@data-zip")[0].split(", ")[-1]
        street_address = poi_html.xpath("@data-address")[0].split(zip_code)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        phone = poi_html.xpath('.//div[@class="store-phone"]/text()')
        phone = phone[-1].strip() if phone else ""
        hoo = poi_html.xpath('.//div[@class="store-hours"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = (
            " ".join(hoo)
            .split("Funcionamento:")[-1]
            .split("funcionamento:")[-1]
            .strip()
        )
        hoo = " ".join([e.strip() for e in hoo.split()])
        latitude = poi_html.xpath("@data-latitude")[0]
        if latitude == "null":
            latitude = ""
        longitude = poi_html.xpath("@data-longitude")[0]
        if longitude == "null":
            longitude = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.sephora.com.br/nossas-lojas/",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code="BR",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
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
