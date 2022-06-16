import json
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://locator.chase.com/search?q={}&l=en&r=100"
    domain = "chase.com"
    hdr = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for code in all_codes:
        code_url = start_url.format(code)
        data = session.get(code_url, headers=hdr).json()
        all_locations = data["response"]["entities"]
        total = data["response"]["count"]
        for p in range(10, total + 10, 10):
            page_url = add_or_replace_parameter(code_url, "offset", str(p))
            response = session.get(page_url, headers=hdr)
            if response.status_code != 200:
                continue
            data = json.loads(response.text)
            all_locations += data["response"]["entities"]

        for poi in all_locations:
            store_url = urljoin(start_url, poi["url"])
            location_name = poi["profile"].get("c_geomodifier")
            if not location_name:
                location_name = poi["profile"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["profile"]["address"]["line1"]
            if poi["profile"]["address"]["line2"]:
                street_address += " " + poi["profile"]["address"]["line2"]
            if poi["profile"]["address"]["line3"]:
                street_address += " " + poi["profile"]["address"]["line3"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["profile"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["profile"]["address"]["region"]
            state = state if state else "<MISSING>"
            zip_code = poi["profile"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["profile"]["address"]["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi["profile"].get("mainPhone", {}).get("display")
            phone = phone if phone else "<MISSING>"
            location_type = poi["profile"]["c_bankLocationType"]
            latitude = poi["profile"]["yextDisplayCoordinate"]["lat"]
            longitude = poi["profile"]["yextDisplayCoordinate"]["long"]
            hoo = []
            if poi["profile"].get("hours"):
                for elem in poi["profile"]["hours"]["normalHours"]:
                    day = elem["day"]
                    if elem["intervals"]:
                        opens = str(elem["intervals"][0]["start"])
                        opens = opens[:-2] + ":" + opens[-2:]
                        closes = str(elem["intervals"][0]["end"])
                        closes = closes[:-2] + ":" + closes[-2:]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
            hours_of_operation = " ".join(hoo) if hoo else ""
            if not hours_of_operation:
                hours_of_operation = "open 24h"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
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
