from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("calibercollision_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.caliber.com/api/es/search"
    payload = {
        "size": 2500,
        "query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": "+contentType:Center +(Center.serviceType:*)"
                    }
                },
                "filter": {
                    "geo_distance": {
                        "distance": "8000.4672km",
                        "center.latlong": {
                            "lat": 38.0293059,
                            "lon": -78.47667810000002,
                        },
                    }
                },
            }
        },
        "sort": [
            {
                "_geo_distance": {
                    "center.latlong": {"lat": 38.0293059, "lon": -78.47667810000002},
                    "order": "asc",
                    "unit": "km",
                    "mode": "min",
                    "distance_type": "arc",
                    "ignore_unmapped": True,
                }
            }
        ],
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "calibercollision.com"
    typ = "<MISSING>"
    country = "US"
    for item in json.loads(r.content)["contentlets"]:
        hours = ""
        state = item["state"]
        name = item["title"]
        city = item["city"]
        lng = item["longitude"]
        lat = item["latitude"]
        zc = item["zip"]
        loc = "https://www.caliber.com/find-a-location/" + item["urlTitle"]
        try:
            phone = item["telephone"]
        except:
            phone = "<MISSING>"
        add = item["address1"]
        store = "<MISSING>"
        if "sunday" not in str(item):
            hours = "Sun: Closed"
        else:
            try:
                hours = (
                    "Sun: "
                    + item["sundayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["sundayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = "Sun: Closed"
        if "monday" not in str(item):
            hours = hours + "; Mon: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Mon: "
                    + item["mondayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["mondayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Mon: Closed"
        if "tuesday" not in str(item):
            hours = hours + "; Tue: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Tue: "
                    + item["tuesdayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["tuesdayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Tue: Closed"
        if "wednesday" not in str(item):
            hours = hours + "; Wed: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Wed: "
                    + item["wednesdayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["wednesdayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Wed: Closed"
        if "thursday" not in str(item):
            hours = hours + "; Thu: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Thu: "
                    + item["thursdayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["thursdayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Thu: Closed"
        if "friday" not in str(item):
            hours = hours + "; Fri: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Fri: "
                    + item["fridayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["fridayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Fri: Closed"
        if "saturday" not in str(item):
            hours = hours + "; Sat: Closed"
        else:
            try:
                hours = (
                    hours
                    + "; Sat: "
                    + item["saturdayHoursOpen"].split(" ")[1].rsplit(":", 1)[0]
                    + "-"
                    + item["saturdayHoursClose"].split(" ")[1].rsplit(":", 1)[0]
                )
            except:
                hours = hours + "; Sat: Closed"
        if hours == "" or "0" not in hours:
            hours = "<MISSING>"
        if "no-location" not in loc:
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
