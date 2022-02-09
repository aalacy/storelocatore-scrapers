from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = (
        "https://api.thrivepetcare.com/location/v1/locations?radius=500&postalcode={}"
    )
    domain = "thrivepetcare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for code in all_codes:
        all_locations = session.get(start_url.format(code), headers=hdr).json()
        for poi in all_locations:
            location_name = poi["name"]
            street_address = poi["addressLine1"].strip()
            if poi["addressLine2"].strip():
                street_address += " " + poi["addressLine2"].strip()
            city = poi["city"]
            state = poi["state"]
            page_url = f'https://www.thrivepetcare.com/locations/{state.lower().replace(" ", "-")}/{city.lower().replace(" ", "-")}/{location_name.lower().replace(".", "").replace(" ", "-")}'
            hoo = []
            for e in poi["workdays"]:
                hoo.append(
                    f'{e["dayOfWeek"]}: {e["openTime"][:-3]} - {e["closeTime"][:-3]}'
                )
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=poi["city"],
                state=state,
                zip_postal=poi["postcode"],
                country_code="",
                store_number=poi["id"],
                phone=poi["mainPhone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
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
