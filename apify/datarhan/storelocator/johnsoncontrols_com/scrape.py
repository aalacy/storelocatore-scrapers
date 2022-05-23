import json

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "johnsoncontrols.com"
    start_url = "https://jcilocationfinderapi-prod.azurewebsites.net/api/locationsapi/getnearbylocations?latitude={}&longitude={}&distance=none&units=mi&iso=en"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Connection": "keep-alive",
        "Host": "jcilocationfinderapi-prod.azurewebsites.net",
        "Origin": "https://www.johnsoncontrols.com",
        "Referer": "https://www.johnsoncontrols.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=50,
    )
    for coord in all_coordinates:
        lat, lng = coord
        response = session.get(start_url.format(lat, lng), headers=headers)
        data = json.loads(response.text)
        data = json.loads(data)

        for poi in data:
            page_url = "https://www.johnsoncontrols.com/locations"
            location_name = poi["Name"]
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            if poi["Address3"]:
                street_address += poi["Address3"]
            if poi["Address4"]:
                street_address += poi["Address4"]
            street_address = (
                street_address.strip().replace(">", "") if street_address else ""
            )
            city = poi["City"]
            state = poi["State"]
            zip_code = poi["PostalCode"]
            country_code = poi["Country"]
            store_number = poi["ID"]
            phone = ""
            if poi["PhoneNumbers"]["Phone"]:
                phone = poi["PhoneNumbers"]["Phone"][0]["Number"]
            location_type = poi["LocationTypeName"]
            latitude = poi["Latitude"]
            longitude = poi["Longitude"]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
                hours_of_operation="",
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
