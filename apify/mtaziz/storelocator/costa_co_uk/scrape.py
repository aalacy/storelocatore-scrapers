from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("costa_co_uk")
DOMAIN = "costa.co.uk"
MISSING = "<MISSING>"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.BRITAIN],
    max_radius_miles=5,
    max_search_results=500,
    granularity=Grain_8(),
)


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    s = set()
    total = 0
    for lat, lng in search:
        x = lat
        y = lng
        url = (
            "https://www.costa.co.uk/api/locations/stores?latitude="
            + str(x)
            + "&longitude="
            + str(y)
            + "&maxrec=500"
        )

        session = SgRequests()
        logger.info(f"Pulling the data for (latitude, longitude) : ({lat, lng}) ")
        r = session.get(url, headers=headers, verify=False, timeout=500)
        logger.info(f"Pulling the data from : {url} ")
        total += len(json.loads(r.content)["stores"])
        for item in json.loads(r.content)["stores"]:
            locator_domain = DOMAIN
            store_number = item["storeNo8Digit"]
            location_type = item["storeType"]
            page_url = MISSING

            # Phone
            phone = item["telephone"]
            if phone == "":
                phone = MISSING

            # Street Address
            add1 = item["storeAddress"]["addressLine1"]
            add = (
                add1
                + " "
                + item["storeAddress"]["addressLine2"]
                + " "
                + item["storeAddress"]["addressLine3"]
            )
            add = add.strip()
            street_address = ""
            if add == "" or add is None:
                street_address = MISSING
            else:
                street_address = add

            # Location Name
            location_name = item["storeNameExternal"]
            if location_name == "":
                location_name = location_type

            # City Name
            city = item["storeAddress"]["city"]
            if city == "":
                city = item["storeAddress"]["addressLine3"]
            if city == "" or city is None:
                city = MISSING
            if city == MISSING:
                city = location_name
            if "Belfast" in location_name:
                city = "Belfast"
            if "Knightswick" in location_name:
                city = "Knightswick"
            if "Lewes" in location_name:
                city = "Lewes"
            if "Belper" in location_name:
                city = "Belper"
            if "Barrow in Furness" in location_name:
                city = "Barrow in Furness"
            if "Washington" in location_name:
                city = "Washington"
            if "Purfleet" in add:
                city = "Purfleet"
            if "Taunton" in location_name:
                city = "Taunton"
            if "Hempstead Valley" in location_name:
                city = "Hempstead Valley"
            if "Belfast" in add:
                city = "Belfast"
            if "Bideford" in location_name:
                city = "Bideford"

            # State
            state = MISSING

            # Zip Postal
            zip_postal = item["storeAddress"]["postCode"]
            if zip_postal == "" or zip_postal is None:
                zip_postal = MISSING

            # Country Code
            country_code = "GB"

            # Latitude and Longitude
            latitude = item["latitude"]
            longitude = item["longitude"]

            # Search location found at
            search.found_location_at(latitude, longitude)

            # Hours of Operation
            soh = item["storeOperatingHours"]
            mon = "Mon: " + soh["openMon"] + "-" + soh["closeMon"]
            tue = "Tue: " + soh["openTue"] + "-" + soh["closeTue"]
            wed = "Wed: " + soh["openWed"] + "-" + soh["closeWed"]
            thu = "Thu: " + soh["openThu"] + "-" + soh["closeThu"]
            fri = "Fri: " + soh["openFri"] + "-" + soh["closeFri"]
            sat = "Sat: " + soh["openSat"] + "-" + soh["closeSat"]
            sun = "Sun: " + soh["openSun"] + "-" + soh["closeSun"]
            hours_of_operation = f"{mon}; {tue}; {wed}; {thu}; {fri}; {sat}; {sun}"
            if ":" not in hours_of_operation:
                hours_of_operation = MISSING

            if (
                "Mon: -; Tue: -; Wed: -; Thu: -; Fri: -; Sat: -; Sun: -"
                in hours_of_operation
            ):
                hours_of_operation = MISSING
            if store_number in s:
                continue
            s.add(store_number)

            addinfo = f"{add}, {city}, {zip_postal}, {country_code}"
            raw_address = addinfo
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        logger.info(
            f'Number of items found: {len(json.loads(r.content)["stores"])} : Total: {total}'
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
