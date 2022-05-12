import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://gnc.com.mx/tiendas-gnc/"
    domain = "gnc.com.mx"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = data = dom.xpath('//script[contains(text(), "locationMap")]/text()')[1]
    data = json.loads(data)

    all_locations = data["*"]["Magento_Ui/js/core/app"]["components"]["locationMap"][
        "locationItems"
    ]
    for poi in all_locations:
        latitude = poi["latitude"] if poi["latitude"] != "0" else ""
        longitude = poi["longitude"] if poi["longitude"] != "0" else ""
        zip_code = poi["zip"]
        if zip_code and zip_code == "sn":
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://gnc.com.mx/tiendas-gnc/",
            location_name=poi["title"],
            street_address=poi["street"],
            city=poi["city"].split(", ")[0],
            state=poi["city"].split(", ")[-1],
            zip_postal=zip_code,
            country_code=poi["country_id"],
            store_number=poi["location_id"],
            phone=poi["phone"],
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
