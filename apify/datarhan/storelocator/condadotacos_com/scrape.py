import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=500&location={}&limit=50&api_key=f758e5b45905bc090af86915406d345c&v=20181201&resolvePlaceholders=true&entityTypes=Restaurant&savedFilterIds=192172006"
    domain = "condadotacos.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi.get("landingPageUrl")
        store_url = store_url if store_url else SgRecord.MISSING
        street_address = poi["address"]["line1"]
        city = poi["address"]["city"]
        city = city if city else SgRecord.MISSING
        state = poi["address"]["region"]
        state = state if state else SgRecord.MISSING
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else SgRecord.MISSING
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else SgRecord.MISSING
        phone = poi.get("mainPhone")
        phone = phone if phone else "<MISSING>"
        hoo = []
        if poi.get("hours"):
            for day, hours in poi["hours"].items():
                if day in ["reopenDate", "holidayHours"]:
                    continue
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hoo.append(f"{day} {opens} - {closes}")
        hoo = [e.strip() for e in hoo if e.strip()][1:]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=poi["meta"]["id"],
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=poi["geocodedCoordinate"]["latitude"],
            longitude=poi["geocodedCoordinate"]["longitude"],
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
