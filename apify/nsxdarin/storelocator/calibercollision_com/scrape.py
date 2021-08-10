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
    url = "https://calibercollision.com/api/locations"
    r = session.get(url, headers=headers)
    website = "calibercollision.com"
    typ = "<MISSING>"
    country = "US"
    for item in json.loads(r.content)["entries"]:
        name = item["title"]
        try:
            hours = str(item["hours"])
        except:
            try:
                hours = "M-F: " + item["newTime_open"] + "-" + item["newTime_closed"]
            except:
                hours = ""
        hours = (
            hours.replace("<br />", "; ")
            .replace("\n", "")
            .replace("<br/>", "; ")
            .replace("<br>", "; ")
        )
        if "SAT" not in hours:
            try:
                hours = (
                    hours
                    + "; "
                    + item["newTime_open_saturday"]
                    + item["newTime_closed_saturday"]
                )
            except:
                pass
        add = item["address_info"][0]["address"].replace('"', "'")
        city = item["address_info"][0]["city"]
        state = item["address_info"][0]["state_province"]
        zc = item["address_info"][0]["zip"]
        try:
            lat = item["address_info"][0]["latitude"]
            lng = item["address_info"][0]["longitude"]
        except:
            lat = "<MISSING>"
            lng = "<MISSING>"
        try:
            phone = item["address_info"][0]["phone"]
        except:
            phone = "<MISSING>"
        loc = (
            "https://calibercollision.com/locate-a-caliber-collision-center/"
            + item["slug"]
        )
        try:
            store = item["location_id"]
        except:
            store = "<MISSING>"
        if hours == "; CLOSED SAT &amp; SUN":
            hours = "M-F: 7:30AM - 5:30PM; CLOSED SAT &amp; SUN"
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace("&amp;", "&")
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
