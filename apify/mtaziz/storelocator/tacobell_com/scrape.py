from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("tacobell_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.tacobell.com"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

session = SgRequests().requests_retry_session(retries=0)


def get_hoo(data_hrs):
    hours = []
    if "openingHours" in data_hrs:
        week_day_opening_list = data_hrs["openingHours"]["weekDayOpeningList"]
        for k in range(len(week_day_opening_list)):
            if week_day_opening_list[k]["closed"] is True:
                hrs_formatted = week_day_opening_list[k]["weekDay"] + " " + "closed"
                hours.append(hrs_formatted)
            else:
                weekday = week_day_opening_list[k]["weekDay"]
                opening_time = week_day_opening_list[k]["openingTime"][
                    "storeDetailsFormattedHour"
                ]
                closing_time = week_day_opening_list[k]["closingTime"][
                    "storeDetailsFormattedHour"
                ]
                hrs_formatted = f"{weekday} {opening_time} - {closing_time}"
                hours.append(hrs_formatted)
    if hours:
        hours = "; ".join(hours)
    else:
        hours = MISSING
    return hours


# The following settings for Dynamic Search produces 6989 stores
# which looks like expected results as far as the store count in the US is concerned

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=20,
    max_search_results=50,
    granularity=Grain_4(),
)


def fetch_data():
    s = set()
    total = 0
    for lat, lng in search:
        url = f"https://www.tacobell.com/store-finder/findStores?latitude={lat}&longitude={lng}&_=1623006716881"
        data_json = session.get(url, headers=headers, timeout=15).json()
        total += len(data_json["nearByStores"])
        for idx, data in enumerate(data_json["nearByStores"]):
            page_url = data["url"]
            page_url = page_url if page_url else MISSING
            logger.info(f"Pulling the data from {idx}: {page_url}")
            locator_domain = DOMAIN
            location_name = ""
            address = data["address"]
            street_address = address["line1"]
            street_address = street_address if street_address else MISSING

            city = address["town"]
            city = city if city else MISSING

            state = address["region"]["isocodeShort"]
            state = state if state else MISSING

            zip_postal = address["postalCode"]
            zip_postal = zip_postal if zip_postal else MISSING

            country_code = address["country"]["isocode"]
            country_code = country_code if country_code else MISSING

            store_number = ""
            store_number = data["storeNumber"]
            if store_number in s:
                continue
            s.add(store_number)
            store_number = store_number if store_number else MISSING

            phone = address["phone"]
            phone = phone if phone else MISSING

            location_type = MISSING
            if store_number:
                location_name = f"Taco Bell {store_number}"
            else:
                location_name = "Taco Bell"

            latitude = data["latitude"]
            latitude = latitude if latitude else MISSING

            longitude = data["longitude"]
            longitude = longitude if longitude else MISSING

            # Found Location at
            if MISSING not in str(latitude) and MISSING not in str(longitude):
                search.found_location_at(latitude, longitude)

            hours_of_operation = get_hoo(data)
            raw_address = address["formattedAddress"]
            raw_address = raw_address if raw_address else MISSING

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

        logger.info(f"found: {len(data_json['nearByStores'])} | total: {total}")


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
