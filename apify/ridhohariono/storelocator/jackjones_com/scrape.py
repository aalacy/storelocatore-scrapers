from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "jackjones.com"
BASE_URL = "https://www.jackjones.com"
LOCATION_URL = "https://www.jackjones.com/nl/en/stores"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_country():
    soup = pull_content(LOCATION_URL)
    country_opt = soup.find("div", {"class": "storelocator__country"}).find_all(
        "option"
    )
    countries = []
    for row in country_opt:
        countries.append(row["value"])
    log.info("Found {} countries".format(len(countries)))
    return countries


def get_state_url(country_list):
    URL = "https://www.jackjones.com/on/demandware.store/Sites-BSE-NL-Site/en_NL/Stores-GetCities?countryCode={country_code}&brandCode=jj"
    URL_STATE = "https://www.jackjones.com/on/demandware.store/Sites-BSE-NL-Site/en_NL/PickupLocation-GetLocations?countryCode={country}&brandCode=jj&postalCodeCity={state}&serviceID=SDSStores&filterByClickNCollect=false"
    result = []
    for row in country_list:
        log.info("Get State information for => " + row)
        data = session.get(URL.format(country_code=row), headers=HEADERS).json()
        log.info("Found {} state on {}".format(len(data), row))
        for state in data:
            result.append(URL_STATE.format(country=row, state=state))
    result = list(set(result))
    log.info("Total state URL = {}".format(len(result)))
    return result


def fetch_data():
    country_list = get_country()
    state_url = get_state_url(country_list)
    locations = []
    for url in state_url:
        data = session.get(url, headers=HEADERS).json()
        if "locations" not in data:
            continue
        for row in data["locations"]:
            page_url = "https://www.jackjones.com/nl/en/stores"
            location_name = handle_missing(row["storeName"])
            if "address2" in row and len(row["address2"]) > 0:
                street_address = "{}, {}".format(
                    row["address1"],
                    row["address2"]
                    + row["houseNumber"]
                    + " "
                    + row["houseNumberExtension"],
                ).strip()
            else:
                street_address = (
                    row["address1"]
                    + row["houseNumber"]
                    + " "
                    + row["houseNumberExtension"]
                ).strip()
            city = handle_missing(row["city"])
            state = "<MISSING>" if "state" not in row else row["state"]
            street_address = street_address.replace(city, "").replace(state, "")
            zip_postal = handle_missing(row["postalCode"])
            country_code = row["country"]
            store_number = row["storeID"]
            location_type = handle_missing(row["brands"][0]["name"])
            phone = (
                handle_missing(re.sub(r"\D+", "", row["phone"]))
                if row["phone"]
                else "<MISSING>"
            )
            latitude = (
                handle_missing(row["latitude"])
                if len(str(row["latitude"])) > 3
                else "<MISSING>"
            )
            longitude = (
                handle_missing(row["longitude"])
                if len(str(row["longitude"])) > 3
                else "<MISSING>"
            )
            hours_of_operation = "<MISSING>"
            raw_address = f"{street_address}, {city}, {state}, {zip_postal}"
            log.info("Append {} => {}".format(location_name, street_address))
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
                raw_address=raw_address,
            )
    return locations


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
