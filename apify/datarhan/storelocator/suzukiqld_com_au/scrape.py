import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://dashboard.digitaldealer.com.au/thirdparty/DealerLocator/SearchPmaLocations/?callback=jQuery183003639374472953749_1637852658752&addressInput=Sydney NSW, Australia&interested_in=find a Dealer&radiusSelect=10000&dealerId=486&latInput=-33.8688197&lngInput=151.2092955&postcode=&_=1637852693044)"
    domain = "suzukiqld.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)

    all_locations = json.loads(response.text.split("8752(")[-1][:-1])
    for poi in all_locations:
        poi = json.loads(poi)
        response = session.get(
            f'https://dashboard.digitaldealer.com.au/thirdparty/DealerLocator/GetLocationInfo/id/{poi["id"]}?callback=jQuery183004728628131860446_1638533567148'
        )
        zip_code = (
            etree.HTML(response.text.split("7148(")[-1][:-1])
            .xpath("//text()")[2]
            .split(",")[-1]
            .strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzukiqld.com.au/locate/",
            location_name=poi["title"],
            street_address=poi["address"],
            city=poi["suburb"],
            state=poi["state"],
            zip_postal=zip_code,
            country_code="AU",
            store_number=poi["id"],
            phone=poi["salesPhone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
