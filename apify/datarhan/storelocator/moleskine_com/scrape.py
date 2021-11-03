import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://aws.servicehub.eurostep.it/api/storelocators/coord/{}/{}"
    domain = "moleskine.com"

    hdr = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/json",
        "Host": "aws.servicehub.eurostep.it",
        "Origin": "https://es.moleskine.com",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lng, lat), headers=hdr)
        if "No stores found" in response.text:
            continue
        data = json.loads(response.text)

        for poi in data["storesList"]:
            store_url = "https://us.moleskine.com/en/store-locator"
            location_name = poi["store_name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["province"]
            state = state if state else "<MISSING>"
            zip_code = poi["zip_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            if state in zip_code:
                zip_code = "-".join(zip_code.split("-")[1:])
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = str(poi["type_of_shop"])
            if location_type == "1":
                location_type = "Moleskin Store"
            elif location_type == "3":
                location_type = "Retailer"
            latitude = poi["location"]["coordinates"][-1]
            longitude = poi["location"]["coordinates"][0]
            hours_of_operation = "<MISSING>"

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
