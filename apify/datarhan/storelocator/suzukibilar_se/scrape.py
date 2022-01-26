import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://suzukibilar.se/aterforsaljare-verkstader#aterforsaljare"
    domain = "suzukibilar.se"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)

    all_locations = data["props"]["pageProps"]["item"]["blocks"]["blocks"][0]["items"]
    for poi in all_locations:

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["title"],
            street_address=poi["reseller"]["address"],
            city=poi["reseller"]["city"],
            state="",
            zip_postal=poi["reseller"]["postalCode"],
            country_code="SE",
            store_number="",
            phone=poi["reseller"]["phone"],
            location_type=poi["reseller"]["type"],
            latitude=poi["reseller"]["latitude"],
            longitude=poi["reseller"]["longitude"],
            hours_of_operation="",
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
