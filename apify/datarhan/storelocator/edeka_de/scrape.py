# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(proxy_country="de")
    start_url = "https://www.edeka.de/api/marketsearch/markets?searchstring={}"
    domain = "edeka.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=1
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        for poi in data["markets"]:
            hoo = []
            for day, hours in poi["businessHours"].items():
                if day == "additionalInfo":
                    continue
                if hours["open"]:
                    opens = hours["from"]
                    closes = hours["to"]
                    hoo.append(f"{day}: {opens} - {closes}")
                else:
                    hoo.append(f"{day}: closed")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi.get("url"),
                location_name=poi["name"],
                street_address=poi["contact"]["address"]["street"],
                city=poi["contact"]["address"]["city"]["name"],
                state=poi["contact"]["address"]["federalState"],
                zip_postal=poi["contact"]["address"]["city"]["zipCode"],
                country_code="DE",
                store_number=poi["id"],
                phone=poi["contact"]["phoneNumber"],
                location_type="",
                latitude=poi["coordinates"]["lat"],
                longitude=poi["coordinates"]["lon"],
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
