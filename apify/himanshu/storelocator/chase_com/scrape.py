from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://locator.chase.com/"
    post_url = "https://locator.chase.com/search?q={}&l=en&offset=0"
    domain = "chase.com"
    hdr = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for code in all_codes:
        url = post_url.format(code)
        data = session.get(url, headers=hdr).json()
        all_locations = data["response"]["entities"]
        total = data["response"]["count"]
        for page in range(10, total + 20, 10):
            url = add_or_replace_parameter(url, "offset", str(page))
            data = session.get(url, headers=hdr).json()
            all_locations += data["response"]["entities"]

        for poi in all_locations:
            store_url = urljoin(start_url, poi["url"])
            location_name = poi["profile"].get("c_geomodifier")
            street_address = poi["profile"]["address"]["line1"]
            if poi["profile"]["address"]["line2"]:
                street_address += " " + poi["profile"]["address"]["line2"]
            if poi["profile"]["address"]["line3"]:
                street_address += " " + poi["profile"]["address"]["line3"]
            city = poi["profile"]["address"]["city"]
            state = poi["profile"]["address"]["region"]
            zip_code = poi["profile"]["address"]["postalCode"]
            country_code = poi["profile"]["address"]["countryCode"]
            store_number = poi["distance"]["id"].split("-")[-1]
            phone = poi["profile"].get("mainPhone", {}).get("display")
            location_type = poi["profile"]["c_bankLocationType"]
            latitude = poi["profile"]["yextDisplayCoordinate"]["lat"]
            longitude = poi["profile"]["yextDisplayCoordinate"]["long"]
            hoo = []
            if poi["profile"].get("hours"):
                for e in poi["profile"]["hours"]["normalHours"]:
                    day = e["day"]
                    if e["isClosed"]:
                        hoo.append(f"{day} Closed")
                    else:
                        opens = str(e["intervals"][0]["start"])
                        opens = opens[:-2] + ":" + opens[-2:]
                        closes = str(e["intervals"][0]["end"])
                        closes = closes[:-2] + ":" + closes[-2:]
                        hoo.append(f"{day} {opens} {closes}")
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

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
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
