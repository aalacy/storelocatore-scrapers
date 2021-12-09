import time
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl


DOMAIN = "regalnails.com"
BASE_URL = "https://regalnails.com"
LOCATION_URL = "https://regalnails.com/salon-locator/"
API_URL = "https://www.regalnails.com/wp-admin/admin-ajax.php?action=store_search&lat="
HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
}
MISSING = "<MISSING>"

session = SgRequests()
log = sglog.SgLogSetup().get_logger("regalnails_com")


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    max_results = 100
    max_distance = 500

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        url = (
            API_URL
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results="
            + str(max_results)
            + "&search_radius="
            + str(max_distance)
            + "&filter=10"
        )

        try:
            res_json = session.get(url, headers=HEADERS).json()
        except:
            time.sleep(2)
            res_json = session.get(url, headers=HEADERS).json()
        for loc in res_json:
            location_name = loc["store"].replace("&#038;", "&")
            phone = loc["phone"].split("/")[0].replace("48w", "48")

            page_url = loc["url"]
            if page_url == "":
                page_url = LOCATION_URL
            latitude = loc["lat"]
            longitude = loc["lng"]
            try:

                search.found_location_at(latitude, longitude)
            except:
                pass

            street_address = loc["address"] + " " + loc["address2"]
            street_address = street_address.strip()

            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            if len(zip_postal.split(" ")) == 2:
                country_code = "CA"
            else:
                if len(zip_postal) == 6:
                    if "4505 E McKellips Road" in street_address:
                        zip_postal = MISSING
                        country_code = "US"

                    else:
                        country_code = "CA"
                        zip_postal = zip_postal[:3] + " " + zip_postal[3:]
                else:
                    country_code = "US"

            store_number = loc["id"].strip()
            if store_number == "":
                store_number = MISSING

            location_type = MISSING
            hours_of_operation = MISSING

            if len(phone) < 5:
                phone = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
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
                raw_address=f"{street_address}, {city}, {state} {zip_postal}",
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            ),
            duplicate_streak_failure_factor=250000,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
