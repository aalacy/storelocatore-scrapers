from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "bbt.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    start_url = "https://www.truist.com/truist-api/locator/locations.json?returnBranchATMStatus=Y&maxResults=100&locationType=BOTH&searchRadius=30&address={}"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=30
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        if not data.get("location"):
            continue
        for poi in data["location"]:
            location_name = poi["locationName"]
            street_address = poi["locationAddress"]["address1"]
            if poi["locationAddress"].get("address2"):
                street_address += " " + poi["locationAddress"]["address2"]
            city = poi["locationAddress"]["city"]
            state = poi["locationAddress"]["state"]
            zip_code = poi["locationAddress"]["zipCode"]
            store_number = poi.get("branchId")
            page_url = f"https://www.truist.com/branch/{state}/{city}/{zip_code}/{street_address.replace(' ', '-')}"
            phone = poi["phone"]
            location_type = poi["locationType"]
            if location_type == "Branch":
                location_type = "Branch/ATM"
            hours_of_operation = []
            if poi.get("lobbyHours"):
                hours_of_operation = poi["lobbyHours"]
            hours_of_operation = (
                ", ".join(hours_of_operation).replace("  ", " ")
                if hours_of_operation
                else "<MISSING>"
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=poi["locationAddress"]["lat"],
                longitude=poi["locationAddress"]["long"],
                hours_of_operation=hours_of_operation,
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
