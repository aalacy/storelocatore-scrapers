from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.be/nl/ajax/dealers"
    domain = "suzuki.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for store_number, poi in data["map_data"]["locations"].items():
        page_url = etree.HTML(poi["infowindow_content"]).xpath("//a/@href")[0]
        page_url = "https://www.suzuki.be" + page_url
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = etree.HTML(poi["infowindow_content"]).xpath(
            '//p[@class="address"]/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        phone = etree.HTML(poi["infowindow_content"]).xpath("//a/text()")[-1].strip()
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Toonzaal")]/following-sibling::div//text()'
        )
        hoo = " ".join(" ".join([e.strip() for e in hoo if e.strip()]).split())

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.suzuki.be/nl/verdelers",
            location_name=poi["title"],
            street_address=raw_address[0],
            city=" ".join(raw_address[1].split()[:-1]),
            state="",
            zip_postal=raw_address[1].split()[-1],
            country_code="BE",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
