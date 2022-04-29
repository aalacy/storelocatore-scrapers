from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("texasroadhouse_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    website = "texasroadhouse.com"
    typ = "<MISSING>"
    for x in range(-170, 170):
        for y in range(-70, 70):
            url = (
                "https://www.texasroadhouse.com/restaurants/near?lat="
                + str(x)
                + "&long="
                + str(y)
                + "&radius=100000&limit=20"
            )
            logger.info(str(y) + " - " + str(x))
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["restaurants"]:
                try:
                    city = item["city"]
                except:
                    city = "<MISSING>"
                try:
                    state = item["state"]
                except:
                    state = "<MISSING>"
                if state == "":
                    state = "<MISSING>"
                try:
                    lat = item["latitude"]
                except:
                    lat = "<MISSING>"
                try:
                    lng = item["longitude"]
                except:
                    lng = "<MISSING>"
                try:
                    loc = "https://togo.texasroadhouse.com/location/" + item["slug"]
                except:
                    loc = "<MISSING>"
                try:
                    add = item["streetaddress"]
                except:
                    add = "<MISSING>"
                try:
                    country = item["country"]
                except:
                    country = "<MISSING>"
                try:
                    phone = item["telephone"]
                except:
                    phone = "<MISSING>"
                try:
                    store = item["extref"]
                except:
                    store = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                try:
                    zc = item["zip"]
                except:
                    zc = "<MISSING>"
                if zc == "":
                    zc = "<MISSING>"
                try:
                    name = item["storename"]
                except:
                    name = "<MISSING>"
                hours = "<MISSING>"
                if name != "<MISSING>":
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
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
