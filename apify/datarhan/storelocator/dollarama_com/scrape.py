import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "dollarama.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    start_url = "https://www.dollarama.com/en-CA/locations/GetDataByCoordinates?longitude={}&latitude={}&distance=500&units=kilometers&amenities=&paymentMethods="
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        expected_search_radius_miles=100,
    )

    for lat, lng in all_coordinates:
        response = session.post(start_url.format(lng, lat), headers=hdr)
        passed = False
        if response.status_code != 200:
            while not passed:
                session = SgRequests()
                response = session.post(start_url.format(lng, lat), headers=hdr)
                if response.status_code == 200:
                    passed = True

        all_poi_data = json.loads(response.text)
        for poi in all_poi_data["StoreLocations"]:
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["ExtraData"]["Address"]["AddressNonStruct_Line1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["ExtraData"]["Address"]["Locality"]
            city = city if city else "<MISSING>"
            state = poi["ExtraData"]["Address"]["Region"]
            state = state if state else "<MISSING>"
            zip_code = poi["ExtraData"]["Address"]["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["ExtraData"]["Address"]["CountryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["LocationNumber"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["ExtraData"]["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["Location"]["type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Location"]["coordinates"][-1]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Location"]["coordinates"][0]
            longitude = longitude if longitude else "<MISSING>"
            store_url = "https://www.dollarama.com/en-CA/locations/{}/{}-{}".format(
                state.replace(" ", "-").replace(".", ""),
                city.replace(" ", "-").replace(".", ""),
                street_address.split(",")[0].replace(" ", "-").replace(".", ""),
            )

            hours_of_operation = []
            days = {
                "Mo": "Monday",
                "Tu": "Tuesday",
                "We": "Wednesday",
                "Th": "Thursday",
                "Fr": "Friday",
                "Sa": "Saturday",
                "Su": "Sunday",
            }

            hours = poi["ExtraData"]["HoursOfOpStruct"]
            hours_of_operation = []
            if hours:
                for key, day_name in days.items():
                    if hours[key]["Ranges"]:
                        start = hours[key]["Ranges"][0]["StartTime"]
                        end = hours[key]["Ranges"][0]["EndTime"]
                        hours_of_operation.append(
                            "{} {} - {}".format(day_name, start, end)
                        )
                    else:
                        hours_of_operation.append("{} closed".format(day_name))

            hours_of_operation = ", ".join(hours_of_operation)

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
