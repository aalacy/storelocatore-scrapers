from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://healthcare.ascension.org/api/locations/search"
    domain = "healthcare.ascension.org"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "geoDistanceOptions": {"location": "New York, NY 10001", "radius": "5500"},
        "facilityName": "",
        "locationType": "",
        "page": 1,
        "pageSize": 10,
        "stateCode": "",
        "filters": {"locationType": [""], "displayName": [""]},
    }
    data = session.post(start_url, headers=hdr, json=frm).json()
    all_locations = data["Results"]
    for page in range(2, data["Pagination"]["TotalPages"] + 1):
        frm["page"] = page
        data = session.post(start_url, headers=hdr, json=frm).json()
        all_locations += data["Results"]

    for poi in all_locations:
        poi = poi["Data"]["Location"]
        page_url = urljoin(start_url, poi["Url"])
        street_address = poi["Address"]["Street"]
        if poi["Address"]["Street2"]:
            street_address += " " + poi["Address"]["Street2"]
        hoo = poi["Hours"]
        if hoo:
            hoo = (
                " ".join([e.strip() for e in hoo if e.strip()])
                .split("Walk-in hours")[0]
                .strip()
            )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["DisplayName"],
            street_address=street_address,
            city=poi["Address"]["City"],
            state=poi["Address"]["State"],
            zip_postal=poi["Address"]["Zip"],
            country_code="",
            store_number="",
            phone=poi["PhoneNumber"],
            location_type=", ".join(poi["LocationTypeTags"]),
            latitude=poi["Address"]["Latitude"],
            longitude=poi["Address"]["Longitude"],
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
