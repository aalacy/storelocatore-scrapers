from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests

from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("totalwine_com")


@retry(stop=stop_after_attempt(5))
def get_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
    }
    session = SgRequests()
    response = session.get(url, headers=headers)
    return response.json()


def fetch_data():
    domain = "totalwine.com"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    start_url = "https://www.totalwine.com/store-finder/api/store/storelocator/v1/storesbystate/{}"
    all_locations = []
    for state in states:
        data = get_url(start_url.format(state))
        if not data.get("stores"):
            logger.info(f"no data found for state: {state}")
            continue
        all_locations += data["stores"]

    for poi in all_locations:
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi.get("address1")
        if street_address:
            if poi.get("address2"):
                street_address = poi["address2"]
        else:
            street_address = poi.get("address2")
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateShort"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["stateIsoCode"]
        country_code = country_code.split("-")[0] if country_code else "<MISSING>"
        store_number = poi["storeNumber"]
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["marketingStatus"] == "COMINGSOON":
            continue
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["storeHours"]["days"]:
            day = elem["dayOfWeek"]
            opens = elem["openingTime"]
            closes = elem["closingTime"]
            if opens == closes:
                hours_of_operation.append(f"{day} closed")
            else:
                hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        store_url = "https://www.totalwine.com/store-info/{}-{}/{}".format(
            poi["state"].lower(), city.replace(" ", "-"), store_number
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
