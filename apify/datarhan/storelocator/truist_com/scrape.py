# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.truist.com/truist-api/locator/locations.json?returnBranchATMStatus=Y&maxResults=100&locationType=BOTH&searchRadius=5&address={}"
    domain = "truist.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=1
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        if not data.get("location"):
            continue
        for poi in data["location"]:
            hoo = (
                " ".join(" ".join(poi["lobbyHours"]).split())
                if poi.get("lobbyHours")
                else ""
            )
            if hoo:
                hoo = hoo.replace("*", "")
                if "Mon: *" in hoo:
                    hoo = ""
            street_address = poi["locationAddress"]["address1"]
            page_url = f'https://www.truist.com/{poi["locationType"].lower()}/{poi["locationAddress"]["state"].lower()}/{poi["locationAddress"]["city"].replace(" ", "-").lower()}/{poi["locationAddress"]["zipCode"].split("-")[0]}/{street_address.lower().replace(" ", "-")}'

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["locationName"],
                street_address=street_address,
                city=poi["locationAddress"]["city"],
                state=poi["locationAddress"]["state"],
                zip_postal=poi["locationAddress"]["zipCode"],
                country_code="",
                store_number=poi.get("locationKey"),
                phone=poi["phone"],
                location_type=poi["locationType"],
                latitude=poi["locationAddress"]["lat"],
                longitude=poi["locationAddress"]["long"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
