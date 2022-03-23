from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("natuzzi_com")


def fetch_data():
    url = "https://api.natuzzi.com/api/storelocator/italia?language=en&store_code=us"
    r = session.get(url, headers=headers)
    website = "natuzzi.com"
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
        state = item["stateProvince"]
        if " - " in city:
            city = city.split(" - ")[0]
        phone = item["phoneNumber"]
        add = item["address1"] + " " + item["address2"]
        add = add.strip()
        lat = item["lat"]
        lng = item["lon"]
        hours = ""
        loc = "https://www.natuzzi.com/us/en/stores/" + store
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
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
