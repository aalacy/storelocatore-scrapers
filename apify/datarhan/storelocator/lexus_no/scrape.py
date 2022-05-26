import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.no/local-retailer/choose-a-dealer/"
    domain = "lexus.no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@data-gt-action="view-dealer"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[contains(text(), "address")]/text()')
        if not data:
            continue
        poi = json.loads(data[0])
        hoo = loc_dom.xpath(
            '//h3[label[contains(text(), "Showroom")]]/following-sibling::ul[1]//text()'
        )
        hoo = [e.replace("&nbsp", "").strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("   Åpningstider")[0].replace("I dag: ", "").strip()
        if hoo == "Åpningstider Mandag  Tirsdag  Onsdag  Torsdag  Fredag  lørdag":
            hoo = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state="",
            zip_postal=poi["address"]["postalCode"],
            country_code="NO",
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
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
