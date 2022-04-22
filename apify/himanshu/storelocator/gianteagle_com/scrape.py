import json

from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_usa
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

logger = SgLogSetup().get_logger("gianteagle_com")


def fetch_data():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
    }
    domain = "gianteagle.com"

    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    isFinish = False
    skip_counter = 0
    while isFinish is False:
        r_locations = session.get(
            "https://www.gianteagle.com/api/sitecore/locations/getlocations?q=&skip="
            + str(skip_counter),
            headers=headers,
            verify=False,
        )
        json_locations = json.loads(r_locations.text)

        if len(json_locations) <= 0:
            logger.info("No more locations")
            break
        logger.info(
            str(skip_counter) + " json_locations == " + str(len(json_locations))
        )
        skip_counter += len(json_locations)

        for location_super_market in json_locations:
            store_number = location_super_market["Id"]
            location_name = location_super_market["Name"]
            raw_address = location_super_market["Address"]["lineOne"]
            if (
                location_super_market["Address"]["lineTwo"] is not None
                and location_super_market["Address"]["lineTwo"].strip() != "-"
            ):
                raw_address += ", " + location_super_market["Address"]["lineTwo"]

            formatted_addr = parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = location_super_market["Address"]["City"]
            state = location_super_market["Address"]["State"]["Abbreviation"]
            zipp = location_super_market["Address"]["Zip"]
            phone = ""
            if location_super_market["TelephoneNumbers"]:
                phone = location_super_market["TelephoneNumbers"][0]["DisplayNumber"]

            number = location_super_market["StoreDisplayName"].split(":")[0].strip()
            page_url = (
                "https://gianteagle.com/stores/"
                + state
                + "/"
                + city
                + "/"
                + location_name.replace(" ", "-").strip()
                + "/"
                + number
            )
            page_url = page_url.replace("-&", "").strip()

            latitude = str(location_super_market["Address"]["Coordinates"]["Latitude"])
            longitude = str(
                location_super_market["Address"]["Coordinates"]["Longitude"]
            )
            location_type = location_super_market["Details"]["Type"]["Name"]

            hours_of_operation = ""
            index = 0
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            for time_period in location_super_market["HoursOfOperation"]:
                if time_period["DayNumber"] == index + 1:
                    hours_of_operation += (
                        days[index] + " " + time_period["HourDisplay"] + " "
                    )
                index += 1

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
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
