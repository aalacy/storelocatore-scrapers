import json
from w3lib.html import remove_tags

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "esso.co.uk"
    start_urls = [
        "https://www.esso.co.uk/en-GB/api/locator/Locations?Latitude1=48.356492210436045&Latitude2=60.94128404594158&Longitude1=-22.645048209150662&Longitude2=16.246553353349338&DataSource=RetailGasStations&Country=GB&Customsort=False",
        "https://www.esso.co.uk/en-GB/api/locator/Locations?Latitude1=50.74676814707322&Latitude2=52.45255064522355&Longitude1=-3.666406883682063&Longitude2=1.195043311630437&DataSource=RetailGasStations&Country=GB&Customsort=False",
    ]

    for start_url in start_urls:
        response = session.get(start_url)
        data = json.loads(response.text)

        for poi in data:
            store_url = (
                "https://www.esso.co.uk/en-gb/find-station/{}--essobranchend-{}".format(
                    poi["City"].lower(), poi["LocationID"]
                )
            )
            location_name = poi["LocationName"]
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += " " + poi["AddressLine2"]
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["StateProvince"]
            state = state if state else "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["Country"]
            store_number = poi["LocationID"]
            phone = poi["Telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["EntityType"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = remove_tags(poi["WeeklyOperatingHours"])

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
