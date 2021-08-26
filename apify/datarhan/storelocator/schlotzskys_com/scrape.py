from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def fetch_data():
    # Your scraper here
    session = SgRequests()
    domain = "schlotzskys.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )

    start_url = "https://www.schlotzskys.com/sitecore/api/v0.1/storelocator/locations?locationname={}"
    headers = {
        "authority": "www.schlotzskys.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    for code in all_codes:
        data = session.get(start_url.format(code), headers=headers).json()
        if not data.get("Locations"):
            continue
        for poi in data["Locations"]:
            store_url = poi["Url"]
            hours_of_operation = []
            for elem in poi["Hours"]:
                if elem["FormattedDayOfWeek"] == "today":
                    continue
                day = elem["FormattedDayOfWeek"]
                opens = elem["Open"]
                close = elem["Close"]
                hours_of_operation.append("{} {} - {}".format(day, opens, close))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=poi["LocationName"],
                street_address=poi["StreetAddress"],
                city=poi["City"],
                state=poi["Region"],
                zip_postal=poi["PostalCode"],
                country_code=poi["CountryName"],
                store_number=poi["StoreNumber"],
                phone=poi["Phone"],
                location_type=SgRecord.MISSING,
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
