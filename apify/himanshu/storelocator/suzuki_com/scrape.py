from bs4 import BeautifulSoup

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzukiauto.com/DealerSearchHandler.ashx?zip={}&distance=100&hasCycles=true&hasAtvs=true&hasScooters=true&hasMarine=true&hasAuto=true&maxResults=90&country=en"
    domain = "suzuki.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        soup = BeautifulSoup(response.text, "lxml")
        all_locations = soup.find_all("dealerinfo")
        for poi_html in all_locations:
            page_url = "https://www.suzukiauto.com/Service%20Provider.aspx"
            street_address = poi_html.find("displayaddress").text
            location_name = poi_html.find("name").text
            city = poi_html.find("city").text
            state = poi_html.find("state").text
            zip_code = poi_html.find("zip").text
            store_number = poi_html.find("dealerid").text
            phone = poi_html.find("phone").text
            latitude = poi_html.find("esriy").text
            longitude = poi_html.find("esrix").text
            hoo = poi_html.find("hours").text

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=poi_html.find("country").text,
                store_number=store_number,
                phone=phone,
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
