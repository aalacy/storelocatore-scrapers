from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bankozarks.com"
    start_url = "https://www.ozk.com/locations/modules/multilocation/?near_location=10001&threshold=4000&geocoder_region=&distance_unit=miles&limit=2000&services__in=&language_code=en-us&published=1&within_business=true"
    data = session.get(start_url).json()

    for poi in data["objects"]:
        hoo = []
        for e in poi["formatted_hours"]["primary"]["days"]:
            hoo.append(f"{e['label']} {e['content']}")
        hoo = " ".join(hoo)
        street_address = poi["street"]
        if poi["street2"]:
            street_address += ", " + poi["street2"]
        location_name = f'{poi["location_name"]} {poi["city"]}'
        location_type = "ATM" if "ATM" in location_name else "BRANCH"

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["location_url"],
            location_name=location_name,
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phones"][0]["number"],
            location_type=location_type,
            latitude=poi["lat"],
            longitude=poi["lon"],
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
