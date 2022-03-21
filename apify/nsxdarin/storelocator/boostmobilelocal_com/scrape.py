from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("boostmobilelocal_com")


def fetch_data():
    url = "https://boostmobilelocal.com/data/locations.json"
    r = session.get(url, headers=headers)
    website = "boostmobilelocal.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("cp1252").encode("utf-8"))
        if '"title":"' in line:
            items = line.split('"title":"')
            for item in items:
                if '"address":"' in item:
                    name = item.split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0].split("  ")[0]
                    loc = item.split('"url":"')[1].split('"')[0]
                    state = (
                        loc.split("https://boostmobilelocal.com/")[1]
                        .split("/")[0]
                        .upper()
                    )
                    city = loc.split("/")[4].replace("-", " ").title()
                    zc = "<MISSING>"
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    hours = ""
                    store = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    r2 = session.get(loc, headers=headers)
                    logger.info(loc)
                    time.sleep(1)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if '"postalCode": "' in line2:
                            zc = line2.split('"postalCode": "')[1].split('"')[0]
                        if 'day"' in line2 and "<" not in line2:
                            day = line2.split('"')[1]
                        if '"opens": "' in line2:
                            ope = line2.split('"opens": "')[1].split('"')[0]
                        if '"closes": "' in line2:
                            clo = line2.split('"closes": "')[1].split('"')[0]
                            hrs = day + ": " + ope + "-" + clo
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if hours == "":
                        hours = "<MISSING>"
                    if state == "LITHONIA":
                        city = "LITHONIA"
                        state = "GA"
                    if "200 Houston" in add:
                        add = add.replace("200 Houston", "200")
                    if "106 E FM 495" in add:
                        lat = "26.207524"
                        lng = "-98.151595"
                    if add == "627":
                        add = "627 Canal Blvd"
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
