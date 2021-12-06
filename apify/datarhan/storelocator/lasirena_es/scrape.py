import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lasirena.es/es/tiendas"
    domain = "lasirena.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//script[contains(text(), "GeoCoordinates")]/text()')
    for poi in all_locations:
        poi = json.loads(poi)
        hoo = []
        for e in poi["openingHoursSpecification"]:
            day = e["dayOfWeek"][0]
            hours = e["opens"]
            if hours:
                hoo.append(f"{day}: {hours}")
            else:
                hoo.append(f"{day}: Closed")
        hoo = " ".join(hoo)
        zip_code = poi["address"]["postalCode"]
        if zip_code == "00000":
            zip_code = ""
        street_address = poi["address"]["streetAddress"].strip().replace(",,", ",")
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=zip_code,
            country_code=poi["address"]["addressCountry"],
            store_number=poi["@id"].split("/")[-1],
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
