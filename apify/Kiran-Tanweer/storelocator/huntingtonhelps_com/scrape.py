from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import json


session = SgRequests()
website = "huntingtonhelps_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.huntingtonhelps.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
        )
        for lat, lng in search:
            search_url = (
                "https://huntingtonhelps.com/location/list-centers?lat="
                + str(lat)
                + "&lng="
                + str(lng)
                + "&limit=200&radius=50"
            )
            stores_req = session.get(search_url, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            locations = soup.find("script")
            locations = str(locations)
            locations = (
                locations.split("centersInRange = ")[1]
                .split("updateMarkers")[0]
                .strip()
            )
            locations = locations.rstrip(";").strip()
            locations = json.loads(locations)
            if locations == []:
                continue
            else:
                for loc in locations:
                    title = loc["center"]["name"]
                    storeid = loc["center"]["id"]
                    url = (
                        "https://huntingtonhelps.com/center/"
                        + loc["center"]["code_url"]
                    )
                    address = loc["location"]
                    phones = loc["phones"]
                    hours = loc["hours"]
                    street = address["address"]
                    city = address["city"]
                    state = address["state"]
                    pcode = address["zipcode"]
                    lat = address["latitude"]
                    lng = address["longitude"]
                    ph = phones["phone_main"]
                    hoo = ""
                    for time in hours:
                        try:
                            days = time["day_of_week"]
                            start = time["open_time"]
                            end = time["close_time"]
                            day = days + " " + start + " - " + end + " "
                            hoo = hoo + day
                        except TypeError:
                            days = hours[time]["day_of_week"]
                            start = hours[time]["open_time"]
                            end = hours[time]["close_time"]
                            day = days + " " + start + " - " + end + " "
                            hoo = hoo + day
                    hoo = hoo.strip()

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=pcode,
                        country_code="US",
                        store_number=storeid,
                        phone=ph,
                        location_type=MISSING,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hoo.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
