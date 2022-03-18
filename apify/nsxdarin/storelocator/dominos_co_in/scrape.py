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

logger = SgLogSetup().get_logger("dominos_co_in")


def fetch_data():
    url = "https://www.dominos.co.in/store-locations/"
    states = []
    cities = []
    allids = []
    places = []
    website = "dominos.co.in"
    typ = "<MISSING>"
    country = "IN"
    r = session.get(url, headers=headers)
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"id":' in line and 'name="advance-search"' in line:
            items = line.split('"id":')
            for item in items:
                if "advance-search" not in item:
                    states.append(
                        item.split(",")[0]
                        + "|"
                        + item.split('"title":"')[1].split('"')[0]
                    )
    for sid in states:
        sname = sid.split("|")[1]
        sidnum = sid.split("|")[0]
        surl = "https://www.dominos.co.in/store-locations/api/get-cities/" + sidnum
        try:
            r2 = session.get(surl, headers=headers)
            logger.info(sid)
            for item in json.loads(r2.content)["data"]:
                cities.append(str(item["id"]) + "|" + sname)
        except:
            pass
    for cid in cities:
        sname = cid.split("|")[1]
        curl = (
            "https://www.dominos.co.in/store-locations/api/get-localities/"
            + cid.split("|")[0]
        )
        try:
            r2 = session.get(curl, headers=headers)
            logger.info(str(cid))
            for item in json.loads(r2.content)["data"]:
                plid = item["link"].rsplit("-", 1)[1]
                if plid not in allids:
                    allids.append(plid)
                    places.append(
                        "https://www.dominos.co.in/store-locations/pizza-delivery-food-restaurants-in-"
                        + item["link"]
                        + "|"
                        + sname
                    )
        except:
            pass
    for curl in places:
        logger.info(curl)
        try:
            r2 = session.get(curl.split("|")[0], headers=headers)
            loc = ""
            hours = "<MISSING>"
            zc = "<MISSING>"
            store = "<MISSING>"
            state = curl.split("|")[1]
            name = ""
            city = ""
            phone = ""
            add = ""
            lat = ""
            lng = ""
            lines = r2.iter_lines()
            for line2 in lines:
                if (
                    '<a class="nav-link" href="https://www.dominos.co.in/store-locations/'
                    in line2
                    and loc == ""
                ):
                    loc = line2.split('href="')[1].split('"')[0]
                    city = loc.split("locations/")[1].split("/")[0].upper()
                    g = next(lines)
                    add = ""
                    phone = ""
                    lat = ""
                    lng = ""
                    name = (
                        g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                    )
                if 'fa fa-map-marker">' in line2 and add == "":
                    next(lines)
                    g = next(lines)
                    add = (
                        g.split('">')[1]
                        .strip()
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("\n", "")
                    )
                if '<i class="fa fa-phone"></i></span>' in line2 and phone == "":
                    g = next(lines)
                    phone = g.split(">")[1].split("<")[0].strip()
                if 'data-lat="' in line2:
                    lat = line2.split('data-lat="')[1].split('"')[0]
                    lng = line2.split('data-lng="')[1].split('"')[0]
                if '<div class="st-section-bottom">' in line2 and name != "":
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
