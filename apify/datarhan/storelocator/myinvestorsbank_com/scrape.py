from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "myinvestorsbank.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=investors_bancorp_answers&api_key=9b0d7ec6abb65a54f2011f7422ed4d5d&v=20190101&version=PRODUCTION&locale=en&input=Find+My+Nearest+ATM&verticalKey=Locations&limit=20&offset=0&facetFilters=%7B%7D&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Fwww.investorsbank.com%2F&source=STANDARD&jsLibVersion=v1.9.2"

    data = session.get(start_url).json()
    total = data["response"]["resultsCount"]
    all_locations = data["response"]["results"]
    for i in range(20, total + 20, 20):
        data = session.get(add_or_replace_parameter(start_url, "offset", str(i))).json()
        all_locations += data["response"]["results"]

    for poi in all_locations:
        poi = poi["data"]
        hoo = []
        for day, hours in poi["hours"].items():
            if type(hours) in [str, list]:
                continue

            if hours.get("isClosed"):
                hoo.append(f"{day} closed")
            else:
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo)
        if poi.get("yextDisplayCoordinate"):
            latitude = poi["yextDisplayCoordinate"]["latitude"]
            longitude = poi["yextDisplayCoordinate"]["longitude"]
        else:
            latitude = poi["geocodedCoordinate"]["latitude"]
            longitude = poi["geocodedCoordinate"]["longitude"]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["website"],
            location_name=poi["name"],
            street_address=poi["address"]["line1"],
            city=poi["address"]["city"],
            state=poi["address"]["region"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["countryCode"],
            store_number=poi["id"],
            phone=poi["mainPhone"],
            location_type=", ".join(poi["services"]),
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
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
