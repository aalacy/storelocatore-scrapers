from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("swarovski_com")


def fetch_data():
    for x in range(-179, 179, 1):
        for y in range(-70, 70, 1):
            Found = True
            count = 0
            while Found and count <= 8:
                try:
                    time.sleep(2)
                    Found = False
                    count = count + 1
                    logger.info(str(y) + "-" + str(x))
                    url = (
                        "https://www.swarovski.com/en-AA/store-finder/list/?allBaseStores=true&geoPoint.latitude="
                        + str(y)
                        + "&geoPoint.longitude="
                        + str(x)
                        + "&radius=500"
                    )
                    try:
                        r = session.get(url, headers=headers)
                        website = "swarovski.com"
                        for item in json.loads(r.content)["results"]:
                            name = item["displayName"]
                            store = item["name"]
                            loc = "https://www.swarovski.com" + item["url"]
                            lat = item["geoPoint"]["latitude"]
                            lng = item["geoPoint"]["longitude"]
                            add = ""
                            if item["address"]["line1"] is not None:
                                add = item["address"]["line1"]
                            if item["address"]["line2"] is not None:
                                add = add + " " + item["address"]["line2"]
                            add = add.strip()
                            city = item["address"]["town"]
                            state = "<MISSING>"
                            zc = item["address"]["postalCode"]
                            phone = item["address"]["phone"]
                            country = item["address"]["country"]["isocode"]
                            typ = item["distributionType"]
                            hours = ""
                            for day in item["openingHours"]["weekDayOpeningList"]:
                                dname = day["weekDay"]
                                dopen = day["openingTime"]["formattedHour"]
                                dclose = day["closingTime"]["formattedHour"]
                                hrs = dname + ": " + dopen + "-" + dclose
                                if day["closed"]:
                                    hrs = dname + ": Closed"
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                            if len(phone) < 6:
                                phone = "<MISSING>"
                            if len(zc) < 2:
                                zc = "<MISSING>"
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
                    except Exception as e:
                        logger.info(f"Failed for {str(x)} - {str(y)}: {e}")
                        pass
                except:
                    Found = True


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
