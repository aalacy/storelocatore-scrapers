from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    domain = "adecco.co.uk"
    start_url = "https://www.adecco.it/trova-agenzie/"

    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.ITALY],
        expected_search_radius_miles=500,
    )
    url = "https://www.adecco.it/globalweb/branch/branchsearch"
    for lat, lng in all_codes:
        frm = {
            "dto": {
                "Latitude": lat,
                "Longitude": lng,
                "MaxResults": "100",
                "Radius": "500",
                "Industry": "ALL",
                "RadiusUnits": "MILES",
            }
        }
        hdr = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        data = session.post(url, json=frm, headers=hdr).json()
        for poi in data["Items"]:
            page_url = urljoin(start_url, poi["ItemUrl"])
            street_address = f'{poi["Address"]} {poi["AddressExtension"]}'
            hoo = []
            for e in poi["ScheduleList"]:
                day = e["WeekdayId"]
                opens = e["StartTime"].split("T")[-1].replace("0:00", "0")
                closes = e["EndTime"].split("T")[-1].replace("0:00", "0")
                hoo.append(f"{day}: {opens} - {closes}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["MetaTitle"],
                street_address=street_address,
                city=poi["City"],
                state=poi["State"],
                zip_postal=poi["ZipCode"],
                country_code=poi["CountryCode"],
                store_number=poi["BranchCode"],
                phone=poi["PhoneNumber"],
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
