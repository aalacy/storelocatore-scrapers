from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
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


LOCATOR_URL = "https://www.pandaexpress.com/location"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("pandaexpress_com")
MAX_WORKERS = 10

hdr_noncookies = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "referer": "https://www.pandaexpress.com/",
}


def get_hours(_, api_url):
    sn = _["extref"]
    hoo = []
    hours_of_operation = ""
    try:
        calendars = _["calendars"]["calendar"][0]["ranges"]
        for cal in calendars:
            s = cal["start"].split(" ")[-1]
            c = cal["end"].split(" ")[-1]
            wd = cal["weekday"]
            wdsc = wd + " " + s + " - " + c
            hoo.append(wdsc)
        hours_of_operation = "; ".join(hoo)
    except Exception as e:
        hours_of_operation = ""
        logger.info(
            f"Fix HoursOfOperation << {e} >> | [StoreNumber:{sn}] | at {api_url}"
        )

    return hours_of_operation


def get_hours_new(_, api_url):
    sn = _["extref"]
    hoo = []
    hours_of_operation = ""
    try:
        calendars = _["calendars"]
        if calendars:
            for i in calendars["calendar"]:
                if i["type"] == "business":
                    for j in i["ranges"]:
                        s = j["start"].split(" ")[-1]
                        c = j["end"].split(" ")[-1]
                        wd = j["weekday"]
                        wdsc = wd + " " + s + " - " + c
                        hoo.append(wdsc)
                    hours_of_operation = "; ".join(hoo)

        else:
            hours_of_operation = ""
    except Exception as e:
        hours_of_operation = ""
        logger.info(
            f"Fix HoursOfOperation << {e} >> | [StoreNumber:{sn}] | at {api_url}"
        )

    return hours_of_operation


def fetch_records(coord, search, current_country, sgw: SgWriter):
    lat_search, lng_search = coord
    # nomnom_calendars_from=20220414&nomnom_calendars_to=20220425
    api_endpoint_url = f"https://nomnom-prod-api.pandaexpress.com/restaurants/near?lat={lat_search}&long={lng_search}&radius=20000&limit=100&nomnom=calendars&nomnom_calendars_from=20220414&nomnom_calendars_to=20220425&nomnom_exclude_extref=99997,99996,99987,99988,99989,99994,11111,8888,99998,99999,0000"
    logger.info(f"pulling from: {api_endpoint_url}")
    with SgRequests() as http:

        try:
            r = http.get(api_endpoint_url, headers=hdr_noncookies)
            logger.info(f"[HTTP {r.status_code} OK!]")
            text = r.text
            logger.info(f"length: {len(text)}")
            if not text:
                logger.info("Response returns empty")
                return
            else:
                js = json.loads(text)
                logger.info("Json loaded")
                rest = js["restaurants"]
                logger.info(f"[FOUND {len(rest)}]")
                if not rest:
                    logger.info("rest is empty!")
                    return
                else:
                    for _ in rest:
                        lat = _["latitude"]
                        lng = _["longitude"]
                        search.found_location_at(float(lat), float(lng))
                        hours = get_hours_new(_, api_endpoint_url)
                        #
                        state = _["state"]
                        city = _["city"]
                        sta = _["streetaddress"]

                        pstate = ""
                        pcity = ""
                        psta = ""

                        # Example page url containing comma
                        # https://www.pandaexpress.com/locations/hi/jbphh/810-williamette-st,-bldg-1786-space-42

                        pcity = city.replace(" ", "-").replace(".", "").replace("#", "")
                        pstate = state
                        locator_url = "https://www.pandaexpress.com/locations/"
                        psta = (
                            sta.replace("#", "")
                            .replace(".", "")
                            .replace(" ", "-")
                            .replace(",", "")
                        )
                        pgurl = locator_url + pstate + "/" + pcity + "/" + psta
                        pgurl = pgurl.lower()
                        item = SgRecord(
                            locator_domain="pandaexpress.com",
                            page_url=pgurl,
                            location_name=_["name"],
                            street_address=sta,
                            city=city,
                            state=state,
                            zip_postal=_["zip"],
                            country_code=_["country"],
                            store_number=_["extref"],
                            phone=_["telephone"],
                            location_type="Restaurant",
                            latitude=_["latitude"],
                            longitude=_["longitude"],
                            hours_of_operation=hours,
                            raw_address="",
                        )
                        sgw.write_row(item)
        except Exception as e:
            logger.info(f"Fix <{e}> at {api_endpoint_url}")


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    search_us = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=10,
        granularity=Grain_8(),
        use_state=False,
    )
    country_us = search_us.current_country().upper()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records, latlng, search_us, country_us, sgw)
            for latlng in search_us
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
