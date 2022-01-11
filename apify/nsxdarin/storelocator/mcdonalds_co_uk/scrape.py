from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()

logger = SgLogSetup().get_logger("mcdonalds_co_uk")


def fetch_data():
    for x in range(49, 61):
        for y in range(-9, 3):
            logger.info(str(x) + "-" + str(y))
            url = (
                "https://www.mcdonalds.com/googleappsv2/geolocation?latitude="
                + str(x)
                + "&longitude="
                + str(y)
                + "&radius=1000&maxResults=1000&country=gb&language=en-gb&showClosed=&hours24Text=Open%2024%20hr"
            )

            headers = {
                "Host": "www.mcdonalds.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en-US;q=0.7,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "X-Requested-With": "XMLHttpRequest",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.mcdonalds.com/us/en-gb/restaurant-locator.html",
            }

            r = session.get(url, headers=headers)
            array = json.loads(r.content)

            country = "GB"
            website = "mcdonalds.com"
            typ = "Restaurant"

            for item in array["features"]:
                try:
                    store = item["properties"]["identifierValue"]
                    loc = (
                        "https://www.mcdonalds.com/gb/en-gb/location/" + store + ".html"
                    )
                    add = item["properties"]["addressLine1"]
                    add = add.strip()
                    city = item["properties"]["addressLine3"]
                    city = city if city else "<MISSING>"
                    state = "<MISSING>"
                    zc = item["properties"]["postcode"]
                    try:
                        phone = item["properties"]["telephone"]
                    except:
                        phone = "<MISSING>"
                    name = item["properties"]["name"]
                    lat = item["geometry"]["coordinates"][1]
                    lng = item["geometry"]["coordinates"][0]
                    try:
                        hours = (
                            "Mon: "
                            + item["properties"]["restauranthours"]["hoursMonday"]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + item["properties"]["restauranthours"]["hoursTuesday"]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item["properties"]["restauranthours"]["hoursWednesday"]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item["properties"]["restauranthours"]["hoursThursday"]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item["properties"]["restauranthours"]["hoursFriday"]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item["properties"]["restauranthours"]["hoursSaturday"]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item["properties"]["restauranthours"]["hoursSunday"]
                        )
                    except:
                        hours = "<MISSING>"
                    if name.strip() == "":
                        name = city.title()
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
                except:
                    pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
