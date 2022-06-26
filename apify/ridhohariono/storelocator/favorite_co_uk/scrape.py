from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import SearchableCountries, DynamicZipAndGeoSearch

DOMAIN = "favorite.com"
LOCATION_URL = "https://favorite.co.uk/store-finder?delivery=0&lat={}&lng={}"
API_URL = "https://favorite.co.uk/ajax/storefinder"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Origin": "https://favorite.co.uk",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": "' Not A;Brand';v='99', 'Chromium';v='102', 'Google Chrome';v='102'",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "X-Requested-With": "XMLHttpRequest",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(retries_with_fresh_proxy_ip=3)

MISSING = SgRecord.MISSING


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
    log.info("Fetching store_locator data")
    search = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_results=5,
    )
    for zipcode, coord in search:
        lat, long = coord
        HEADERS["Referer"] = LOCATION_URL.format(lat, long)
        payloads = {
            "action": "init",
            "is_reload": False,
            "postcode": zipcode,
            "delivery": 0,
            "lat": lat,
            "lng": long,
        }
        log.info(f"Pull data => {zipcode} = {lat}, {long}")
        try:
            stores = session.post(
                API_URL,
                headers=HEADERS,
                data=payloads,
            ).json()
        except:
            search.found_nothing()
            continue
        if not stores["result"]:
            search.found_nothing()
            continue
        soup = bs(stores["html"], "lxml")
        latlong = re.findall(
            r".*\?daddr=(\-?[0-9]+\.[0-9]+,\-?[0-9]+\.[0-9]+)",
            soup.find("script").string,
        )
        main = soup.find_all("div", {"class": "row row-store mb0"})
        if not main:
            search.found_nothing()
            continue
        index = 0
        for row in main:
            page_url = LOCATION_URL.format(lat, long)
            content = row.find("div", {"class": "col-12 mb0"})
            location_name = (
                content.find("div", {"class": "store-name"})
                .get_text(strip=True, separator=",")
                .split(",")[0]
            )
            raw_address = " ".join(
                ", ".join(
                    content.find("div", {"class": "store-name"})
                    .get_text(strip=True, separator=",")
                    .split(",")[2:]
                )
                .replace("\n", " ")
                .split()
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            if "4 Broadwalk" in raw_address:
                street_address = "4 Broadwalk"
                city = "Crawley"
            country_code = "UK"
            store_number = MISSING
            phone = row.find(
                "a", {"class": "store-no", "href": re.compile(r"tel\:\/\/.*")}
            )
            if not phone:
                phone = MISSING
            else:
                phone = phone.text
            day_hours = content.find("ul", {"class": "opening-times"}).find_all(
                "li", {"class": False}
            )
            hours = []
            for x in day_hours:
                hoo = x.find("span", {"class": "ot"}).text.strip()
                hours.append(hoo)
            if all(value == "Closed" for value in hours):
                location_type = "CLOSED"
            else:
                location_type = "OPEN"
            hours_of_operation = (
                ", ".join(
                    content.find("ul", {"class": "opening-times"})
                    .get_text(strip=True, separator=",")
                    .split(",")[1:]
                )
                .replace("Delivery, ", "")
                .strip()
            )
            try:
                latitude = latlong[index].split(",")[0]
                longitude = latlong[index].split(",")[1]
                search.found_location_at(latitude, longitude)
            except:
                latitude = MISSING
                longitude = MISSING
                search.found_location_at(lat, long)
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
            index += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
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
