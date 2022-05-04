from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("redrobin_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.redrobin.com/locations"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<li><a href="' in line:
            items = line.split('<li><a href="')
            for item in items:
                if "<!DOCTYPE html>" not in item:
                    stub = item.split('"')[0]
                    if "https" in stub:
                        lurl = stub
                    else:
                        lurl = "https://redrobin.com" + item.split('"')[0].replace(
                            ".", "-"
                        )
                    if lurl != "https://redrobin.com/locations/" and "/fl/" in lurl:
                        if "fl/st.petersburg/tyrone-mall-553" in lurl:
                            lurl = (
                                "https://locations.redrobin.com/fl/st-petersburg/553/"
                            )
                        locs.append(lurl)
    for loc in locs:
        try:
            logger.info(loc)
            country = "US"
            website = "redrobin.com"
            typ = "Restaurant"
            hours = ""
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = ""
            phone = ""
            lat = ""
            lng = ""
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '<link rel="canonical" href="' in line2:
                    store = (
                        line2.split('<link rel="canonical" href="')[1]
                        .split('/"')[0]
                        .rsplit("/", 1)[1]
                    )
                if "<h1>" in line2:
                    name = line2.split("<h1>")[1].split("<")[0]
                if '"addressRegion": "' in line2:
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                    lat = line2.split('"latitude": "')[1].split('"')[0]
                    lng = line2.split('"longitude": "')[1].split('"')[0]
                    phone = line2.split('"telephone": "')[1].split('"')[0]
                if '<p class="day">' in line2:
                    day = line2.split('<p class="day">')[1].split("<")[0]
                if '<p class="hours">' in line2:
                    hrs = day + " " + line2.split('<p class="hours">')[1].split("<")[0]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if "/bc/" in loc:
                country = "CA"
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
