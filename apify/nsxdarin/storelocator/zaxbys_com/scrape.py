import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("zaxbys_com")


def fetch_location(loc, retry=0):
    try:
        logger.info(loc)
        website = "zaxbys.com"
        typ = "<MISSING>"
        country = "US"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        soup = BeautifulSoup(r2.text)
        queries = json.loads(
            re.sub(r"&q;", '"', soup.find("script", {"id": "serverApp-state"}).string)
        )
        for key, value in queries.items():
            if re.search(r"getstore", key):
                data = value["data"]

                street_address = data["Address"]
                city = data["City"]
                state = data["State"]
                zc = data["Zip"]
                lat = data["Latitude"]
                lng = data["Longitude"]
                name = street_address

                phone = data["Phone"]

                hours = [
                    dayhour for dayhour in re.split(r";", data["StoreHours"]) if dayhour
                ]
                hours_of_operation = []
                days = {
                    "1": "Monday",
                    "2": "Tuesday",
                    "3": "Wednesday",
                    "4": "Thursday",
                    "5": "Friday",
                    "6": "Saturday",
                    "7": "Sunday",
                }
                for hour in hours:
                    day_num, start, end = hour.split(",")
                    day = days[day_num]
                    hours_of_operation.append(f"{day}: {start}-{end}")

                if "ae/quebec/" in loc:
                    country = "CA"
                if city != "" and "q;Website&" not in hours:
                    return SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=",".join(hours_of_operation),
                    )
    except:
        if retry < 3:
            return fetch_location(loc, retry + 1)


def fetch_data():
    locs = []
    url = "https://www.zaxbys.com/sitemap.xml"
    r = session.get(url, headers=headers)

    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.zaxbys.com/locations/" in line:
            items = line.split("<loc>https://www.zaxbys.com/locations/")
            for item in items:
                if "<xmp><urlset" not in item:
                    locs.append(
                        "https://www.zaxbys.com/locations/" + item.split("<")[0]
                    )

    fetch_location("https://www.zaxbys.com/locations/ut/lehi/2931-w-maple-loop-dr")
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_location, loc)
            for loc in locs
            if loc != "https://www.zaxbys.com/locations/"
        ]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
