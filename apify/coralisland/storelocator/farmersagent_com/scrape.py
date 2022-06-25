# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://agents.farmers.com/search.html?q={}&qp={}&country=US&l=en"
    domain = "farmersagent.com"
    hdr = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=5
    )
    for code in all_codes:
        data = session.get(start_url.format(code, code), headers=hdr).json()
        if not data["response"]["entities"]:
            all_codes.found_nothing()
        for poi in data["response"]["entities"]:
            street_address = poi["profile"]["address"]["line1"]
            sa_2 = poi["profile"]["address"]["line2"]
            if sa_2:
                street_address += ", " + sa_2
            sa_3 = poi["profile"]["address"]["line3"]
            if sa_3:
                street_address += ", " + sa_3
            hoo = []
            if poi["profile"].get("hours"):
                for e in poi["profile"]["hours"]["normalHours"]:
                    if e["intervals"]:
                        opens = (
                            str(e["intervals"][0]["start"])[:-2]
                            + ":"
                            + str(e["intervals"][0]["start"])[-2:]
                        )
                        closes = (
                            str(e["intervals"][0]["end"])[:-2]
                            + ":"
                            + str(e["intervals"][0]["end"])[-2:]
                        )
                        hoo.append(f'{e["day"]}: {opens} - {closes}')
                    else:
                        hoo.append(f'{e["day"]}: closed')
            hoo = ", ".join(hoo)
            latitude = poi["profile"]["yextDisplayCoordinate"]["lat"]
            longitude = poi["profile"]["yextDisplayCoordinate"]["long"]
            all_codes.found_location_at(latitude, longitude)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["profile"]["websiteUrl"],
                location_name=poi["profile"]["name"],
                street_address=street_address,
                city=poi["profile"]["address"]["city"],
                state=poi["profile"]["address"]["region"],
                zip_postal=poi["profile"]["address"]["postalCode"],
                country_code=poi["profile"]["address"]["countryCode"],
                store_number=poi["profile"]["c_farmersLocationID"],
                phone=poi["profile"]["mainPhone"]["display"],
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
