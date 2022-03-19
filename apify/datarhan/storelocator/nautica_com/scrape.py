from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "nautica.com"
    start_url = "https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-GetNearestStores?postalCode={}&countryCode=US&distanceUnit=mi&maxdistance=100"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for code in all_codes:
        data = session.get(start_url.format(code)).json()
        for poi in data.values():
            page_url = "https://www.nautica.com/store-details?storeid={}".format(
                poi["storeID"]
            )
            location_name = poi["name"]
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            city = poi["city"]
            state = poi["stateCode"]
            zip_code = poi["postalCode"]
            country_code = poi["countryCode"]
            store_number = poi["storeID"]
            phone = poi["phone"]
            phone = phone.split("<")[0] if phone else "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = etree.HTML(poi["storeHours"])
            if hours_of_operation:
                hours_of_operation = hours_of_operation.xpath("//text()")[1:]
                hours_of_operation = [
                    elem.strip() for elem in hours_of_operation if elem.strip()
                ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )

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
                location_type="",
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
