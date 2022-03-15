from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("eyeglassworld_com")


def fetch_data():
    locs = []
    url = "https://www.eyeglassworld.com/store/store_sitemap.xml"
    r = session.get(url, headers=headers)
    website = "eyeglassworld.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.eyeglassworld.com/store-list/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        HFound = False
        try:
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '"name" : "' in line2:
                    name = line2.split('"name" : "')[1].split('"')[0]
                if '"streetAddress" : "' in line2:
                    add = line2.split('"streetAddress" : "')[1].split('"')[0]
                if '"addressLocality"  :  "' in line2:
                    city = line2.split('"addressLocality"  :  "')[1].split('"')[0]
                if '"addressRegion" : "' in line2:
                    state = line2.split('"addressRegion" : "')[1].split('"')[0]
                if '"postalCode" : "' in line2:
                    zc = line2.split('"postalCode" : "')[1].split('"')[0]
                if '"telephone" : "' in line2:
                    phone = line2.split('"telephone" : "')[1].split('"')[0]
                if '"openingHours" : [' in line2:
                    HFound = True
                if HFound and "]" in line2:
                    HFound = False
                if HFound and '"' in line2 and "[" not in line2:
                    hrs = line2.split('"')[1]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "Temporarily Closed"
            add = (
                add.replace("Suite", " Suite").replace("  ", " ").replace("&amp;", "&")
            )
            if add != "":
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
