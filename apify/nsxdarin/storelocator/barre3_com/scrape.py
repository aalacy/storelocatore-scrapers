from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("barre3_com")


def fetch_data():
    url = "https://api.storerocket.io/api/user/jN49m3n4Gy/locations"
    r = session.get(url, headers=headers)
    website = "barre3.com"
    typ = "<MISSING>"
    hours = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["results"]["locations"]:
        store = item["id"]
        loc = "https://barre3.com/studio-locations/" + item["slug"]
        add = item["address_line_1"]
        try:
            add = add + " " + item["address_line_2"]
        except:
            pass
        city = item["city"]
        state = item["state"]
        zc = item["postcode"]
        phone = item["phone"]
        lat = item["lat"]
        lng = item["lng"]
        name = item["name"]
        add = add.strip()
        if add == "":
            add = "<MISSING>"
        if "939-2510" in str(phone):
            phone = "480-939-2510"
        if "811.2828" in str(phone):
            phone = "811.2828"
        if phone is None:
            phone = "<MISSING>"
        if "R3 Level," in str(add):
            add = "R3 Level, Power Plant Mall, Rockwell Center"
        if state != "":
            if zc != "":
                if add == "":
                    add = "<MISSING>"
                if "westfield" in loc:
                    name = name + " - Coming Soon"
                if "Asia" not in str(item["timezone"]):
                    if " (" in zc:
                        zc = zc.split(" (")[0]
                    if " " in zc:
                        country = "CA"
                    else:
                        country = "US"
                    if add == "" or add is None:
                        add = "<MISSING>"
                    if phone == "NULL":
                        phone = "<MISSING>"
                    if "locations/huntsville" in loc:
                        phone = "5032068396"
                    if "sioux-falls" in loc:
                        phone = "605.271.6908"
                    if "south-tampa" in loc:
                        phone = "5032068396"
                    if "dc-spring-valley" in loc:
                        add = "4900 Massachusetts Ave NW"
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
