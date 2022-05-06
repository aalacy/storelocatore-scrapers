from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
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

max_workers = 32


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


def parse_cn(raw_address):
    raw_address = raw_address.replace("中国", "")
    state = street_address = city = ""
    if "澳门" in raw_address:
        city = "澳门"
        street_address = raw_address.replace("澳门", "")
    if "香港" in raw_address:
        city = "香港"
        street_address = raw_address.replace("香港", "")
    if "省" in raw_address:
        state = raw_address.split("省")[0] + "省"
        raw_address = raw_address.split("省")[-1]
    if "自治区" in raw_address:
        state = raw_address.split("自治区")[0] + "自治区"
        raw_address = raw_address.split("自治区")[-1]
    if "内蒙古" in raw_address:
        state = "内蒙古"
        raw_address = raw_address.replace("内蒙古", "")
    if "自治州" in raw_address:
        state = raw_address.split("自治州")[0] + "自治州"
        raw_address = raw_address.split("自治州")[-1]

    if "路" in city:
        _cc = city.split("路")
        city = _cc[-1]
        street_address = _cc[0] + "路" + street_address
    if "号" in city:
        _cc = city.split("号")
        city = _cc[-1]
        street_address = _cc[0] + "号" + street_address
    if "区" in city:
        _cc = city.split("区")
        city = _cc[-1]
        street_address = _cc[0] + "区" + street_address

    if "市" in raw_address:
        _ss = raw_address.split("市")
        street_address = _ss[-1]
        city = _ss[0]
        if "市" not in city:
            city += "市"

    return street_address, city, state


def fetch_data():
    with SgRequests() as http:
        for a in range(1, 11):
            for b in range(26):
                for c in range(20):
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

                        zip_postal = addr.get("zipcode")
                        if addr["country_code"] == "CN":
                            street_address, city, state = parse_cn(raw_address)
                        else:
                            street_address = " ".join(addr["lines"]).strip()
                            city = addr["city"]
                            zip_postal = addr.get("zipcode")
                            if "Excellium" in city:
                                city = ""
                            if city and city.isdigit():
                                city = ""

                            if city:
                                city = city.split(",")[0]

                        # clean the street_address
                        if street_address:
                            if street_address.lower() in [
                                "-",
                                "#n/a",
                                "republic of korea",
                            ]:
                                street_address = ""
                            if phone and street_address == phone:
                                street_address = ""
                            if " km " in street_address:
                                street_address = street_address.split(" km")[-1].strip()

                            _street = street_address.split()
                            if _street[-1].strip() == addr["country_code"]:
                                del _street[-1]
                            if city and _street[-1].strip() == city:
                                del _street[-1]

                            street_address = " ".join(_street)

                        latitude = loc["geometry"]["coordinates"][1]
                        longitude = loc["geometry"]["coordinates"][0]
                        if latitude:
                            street_address = street_address.replace(
                                str(latitude), ""
                            ).strip()
                        if longitude:
                            street_address = street_address.replace(
                                str(longitude), ""
                            ).strip()

                        yield SgRecord(
                            page_url=base_url,
                            store_number=_["store_id"],
                            location_name=_["name"],
                            street_address=street_address.strip(),
                            city=city,
                            zip_postal=zip_postal,
                            country_code=addr["country_code"],
                            phone=phone,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation="; ".join(hours),
                            location_type=_["user_properties"]["brand"],
                            locator_domain=locator_domain,
                            raw_address=raw_address,
                        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
