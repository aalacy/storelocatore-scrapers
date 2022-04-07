from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://api.storyblok.com/v2/cdn/stories/shared/locations?cv=1646613151&token=Q7Dh7rPT709Qyx0QKMqUwwtt&version=published"
    domain = "teamexos.com"

    data = session.get(start_url).json()
    for poi in data["story"]["content"]["body"][0]["items"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.teamexos.com/location/contact",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="",
            store_number="",
            phone="",
            location_type=", ".join(poi["facilityTypes"]),
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
