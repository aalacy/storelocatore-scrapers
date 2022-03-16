from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    domain = "pagoda.com"
    session = SgRequests()

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=5
    )
    for code in all_codes:
        url = f"https://www.banter.com/store-finder/find?q={code}&page=0"
        data = session.get(url).json()
        if not data.get("data"):
            continue
        for poi in data["data"]:
            page_url = urljoin("https://www.banter.com/", poi["url"])
            street_address = poi["line1"]
            if poi["line2"]:
                street_address += ", " + poi["line2"]
            hoo = []
            for day, hours in poi["openings"].items():
                hoo.append(f"{day} {hours}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["displayName"],
                street_address=street_address,
                city=poi["town"],
                state=poi["regionIsoCodeShort"],
                zip_postal=poi["postalCode"],
                country_code="",
                store_number=poi["name"],
                phone=poi["phone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
