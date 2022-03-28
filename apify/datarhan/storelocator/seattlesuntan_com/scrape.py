# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://sst.atomicinfotech.com/api.php/storelookup/liststores?callback=jQuery31002782155807761054_1633711301426&Col=Address, City, Closed, Email, Hours, Hours2, Hours3, Latitude, Longitude, Phone, ShowOnWebsite,State, StoreName, StoreNum, webDisplayName, Zip"
    domain = "seattlesuntan.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = response.text.split("426(")[-1][:-2]
    data = json.loads(data)

    for store_number, poi in data.items():
        page_url = (
            f'https://seattlesuntan.com/locations?location={poi["StoreName"]}'.replace(
                " ", "%20"
            )
        )
        hoo = f'Monday - Friday: {poi["Hours"]}, Saturday: {poi["Hours2"]}, Sunday: {poi["Hours3"]}'

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["webDisplayName"],
            street_address=poi["Address"],
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["Zip"],
            country_code="",
            store_number=store_number,
            phone=poi["Phone"],
            location_type="",
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
