from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/ro/ro/stores/"
    domain = "ikea.com/ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[div[div[div[iframe]]]]")
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//div[@data-pub-type="button-link"]/a/@href')[0]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h2/strong/text()")[0]
        raw_adr = poi_html.xpath(
            './/h4[strong[contains(text(), "Adresa")]]/following-sibling::p/text()'
        )[0].split(", ")
        street_address = ", ".join(raw_adr[:-1])
        zip_code = (
            poi_html.xpath(
                './/h4[strong[contains(text(), "Adresa")]]/following-sibling::p/text()'
            )[-1]
            .split(":")[-1]
            .strip()
            .split("poştal ")[-1]
        )
        geo = (
            poi_html.xpath(".//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!3m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath('//p[strong[contains(text(), "Orar magazin")]]/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_adr[-1],
            state="",
            zip_postal=zip_code,
            country_code="RO",
            store_number="",
            phone="",
            location_type="",
            latitude=geo[1].split("!")[0],
            longitude=geo[0].split("!")[0],
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
