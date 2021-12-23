from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time
from tenacity import retry, stop_after_attempt
import tenacity
import random


@retry(stop=stop_after_attempt(8), wait=tenacity.wait_fixed(8))
def get_response(url):
    with SgRequests(proxy_country="gb") as http:
        response = http.get(url)
        time.sleep(random.randint(10, 15))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


logger = SgLogSetup().get_logger("natuzzi_co_uk")


def fetch_data():
    session = SgRequests(proxy_country="gb")
    urls = [
        "https://api.natuzzi.com/api/storelocator/editions?language=en&store_code=gb",
        "https://api.natuzzi.com/api/storelocator/italia?language=en&store_code=gb",
    ]
    for url in urls:
        r = session.get(url)
        logger.info(f"r: {r}")
        website = "natuzzi.co.uk"
        typ = "<MISSING>"
        loc = "<MISSING>"
        logger.info("Pulling Stores")
        for item in json.loads(r.content):
            store = item["slug"]
            name = item["name"]
            typ = item["type"]
            zc = item["zipCode"]
            city = item["city"]
            country = item["country"]
            try:
                state = item["stateProvince"]
            except:
                state = "<MISSING>"
            if " - " in city:
                city = city.split(" - ")[0]
            phone = item["phoneNumber"]
            add = item["address1"] + " " + item["address2"]
            add = add.strip()
            lat = item["lat"]
            lng = item["lon"]
            hours = ""
            loc = "https://www.natuzzi.com/us/en/stores/" + store
            logger.info(loc)
            r2 = session.get(loc)
            st = r2.status_code
            logger.info(f"r2: {st}")
            if st != 200:
                r2 = get_response(loc)

            time.sleep(10)
            for line2 in r2.iter_lines():
                if '"openingTimes":' in line2:
                    days = line2.split('"openingTimes":')[1].split('"key":"')
                    for day in days:
                        if ',"value":"' in day:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split(',"value":"')[1].split('"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if hours == "":
                hours = "<MISSING>"
            yield SgRecord(
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
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
