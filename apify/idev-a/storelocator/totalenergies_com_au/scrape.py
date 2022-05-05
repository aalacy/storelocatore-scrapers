from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("totalenergies")

_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://totalenergies.com.au",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://totalenergies.com.au/"
base_url = "https://totalenergies.com.au/contact-us/distributors"
json_url = "https://api.woosmap.com/tiles/{}-{}-{}.grid.json?key=mapstore-prod-woos&_=1637156671"
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}

max_workers = 24


def fetchConcurrentSingle(store):
    logger.info(store["store_id"])
    url = f"https://api.woosmap.com/stores/{store['store_id']}?key=mapstore-prod-woos"
    loc = request_with_retries(url).json()
    _ = loc["properties"]
    return loc, _


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as http:
        for a in range(1, 11):
            for b in range(20):
                for c in range(10):
                    logger.info(f"{a, b, c}")
                    try:
                        data = http.get(
                            json_url.format(a, b, c), headers=_headers
                        ).json()["data"]
                    except:
                        break
                    logger.info(f"[{a, b, c}] {len(data.keys())} found")
                    stores = [store for kk, store in data.items()]
                    for loc, _ in fetchConcurrentList(stores):
                        addr = _["address"]
                        raw_address = " ".join(addr["lines"])
                        raw_address += " " + addr["city"]
                        raw_address += " " + addr.get("zipcode")
                        raw_address += " " + addr["country_code"]
                        hours = []
                        for key, hh in _["weekly_opening"].items():
                            if key.isdigit() and hh["hours"]:
                                times = []
                                for tt in hh["hours"]:
                                    times.append(f"{tt['start']} - {tt['end']}")
                                hours.append(f"{hr_obj[key]}: {','.join(times)}")

                        phone = _.get("contact").get("phone")
                        if phone and ("contact" in phone.lower() or phone == "-"):
                            phone = ""

                        if phone:
                            phone = phone.split(",")[0]

                        city = addr["city"]
                        zip_postal = addr.get("zipcode")
                        if "Excellium" in city:
                            city = ""
                        if city and city.isdigit():
                            city = ""

                        if city:
                            city = city.split(",")[0]

                        yield SgRecord(
                            page_url=base_url,
                            store_number=_["store_id"],
                            location_name=_["name"],
                            street_address=" ".join(addr["lines"]),
                            city=city,
                            zip_postal=zip_postal,
                            country_code=addr["country_code"],
                            phone=phone,
                            latitude=loc["geometry"]["coordinates"][1],
                            longitude=loc["geometry"]["coordinates"][0],
                            hours_of_operation="; ".join(hours),
                            location_type=_["user_properties"]["brand"],
                            locator_domain=locator_domain,
                            raw_address=raw_address,
                        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
