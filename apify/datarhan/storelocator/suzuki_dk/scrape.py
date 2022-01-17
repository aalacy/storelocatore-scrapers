import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://suzuki.dk/find-forhandler"
    domain = "suzuki.dk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//dealer-map/@*[contains(name(), "dealers")]')[0]
    all_locations = json.loads(all_locations)
    for poi in all_locations:
        if not poi["saleAndService"]:
            continue
        page_url = f'https://suzuki.dk/find-forhandler/{poi["slug"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[h3[contains(text(), "ningstider Salgs")]]/p//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state="",
            zip_postal=poi["postalCode"],
            country_code="DK",
            store_number=poi["dealerNumber"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["position"]["lat"],
            longitude=poi["position"]["lng"],
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
