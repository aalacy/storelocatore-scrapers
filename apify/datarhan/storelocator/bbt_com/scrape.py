import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bbt.com"
    start_url = "https://www.bbt.com/locator/search.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//select[@id="branch-locator__state-select"]/option/@value')
    for state in all_states:
        all_cities = session.get(
            f"https://www.bbt.com/clocator/getCities.do?state={state}"
        ).json()
        for city in all_cities["cities"]:
            url = f"https://www.bbt.com/clocator/searchLocations.do?address={city}, {state}&type=branch&services="
            response = session.get(url)
            if response.text.endswith("}}"):
                data = json.loads(response.text)
            elif response.text.endswith('"'):
                data = json.loads(response.text + "}}")
            else:
                data = json.loads(response.text + '"}}')

            for poi in data["locationsFound"]:
                store_url = "<MISSING>"
                location_name = poi["locationName"]

                location_name = location_name if location_name else "<MISSING>"
                street_address = poi["address1"]
                if poi["address2"]:
                    street_address += " " + poi["address2"]
                street_address = street_address if street_address else "<MISSING>"
                city = poi["city"]
                city = city if city else "<MISSING>"
                state = poi["state"]
                state = state if state else "<MISSING>"
                zip_code = poi["zip"]
                zip_code = zip_code if zip_code else "<MISSING>"
                country_code = "<MISSING>"
                store_number = poi["centerATMNumber"]
                store_number = store_number if store_number else "<MISSING>"
                phone = poi["phone"]
                phone = phone if phone else "<MISSING>"
                location_type = poi["locationType"]
                if location_type == "Branch":
                    location_type = "Branch/ATM"
                location_type = location_type if location_type else "<MISSING>"
                latitude = poi["latitude"]
                latitude = latitude if latitude else "<MISSING>"
                longitude = poi["longitude"]
                longitude = longitude if longitude else "<MISSING>"
                hours_of_operation = poi["lobbyHours"]
                hours_of_operation = (
                    ", ".join(hours_of_operation).replace("  ", " ")
                    if hours_of_operation
                    else "<MISSING>"
                )

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
