from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "lexus.com"
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
    )
    for code in zips:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }
        data = session.get(
            f"https://www.lexus.com/rest/lexus/dealers?experience=dealers&dealerSearchStrategy=expandFallback&zip={code}",
            headers=headers,
        )
        if data.status_code != 200:
            continue
        data = data.json()
        if not data.get("dealers"):
            continue
        for poi in data["dealers"]:
            hoo = ""
            if poi.get("hoursOfOperation", {}).get("Sales"):
                hoo = []
                for day, hours in poi["hoursOfOperation"]["Sales"].items():
                    hoo.append(f"{day}: {hours}")
                hoo = " ".join(hoo)
            store_number = poi["id"]
            page_url = (
                f"https://www.lexus.com/dealers/{store_number}-"
                + poi["dealerDetailSlug"]
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["dealerName"],
                street_address=poi["dealerAddress"]["address1"],
                city=poi["dealerAddress"]["city"],
                state=poi["dealerAddress"]["state"],
                zip_postal=poi["dealerAddress"]["zipCode"],
                country_code="",
                store_number=store_number,
                phone=poi["dealerPhone"],
                location_type="",
                latitude=poi["dealerLatitude"],
                longitude=poi["dealerLongitude"],
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
