from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("oldnavy_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    alllocs = []
    stnames = []
    states = []
    url = "https://oldnavy.gap.com/stores"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="/stores/' in line:
            stname = line.split('<a href="/stores/')[1].split('"')[0]
            if stname not in stnames:
                stnames.append(stname)
                states.append("https://oldnavy.gap.com/stores/" + stname)
    for state in states:
        cities = []
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a href="/stores/' in line2:
                cities.append(
                    "https://oldnavy.gap.com" + line2.split('href="')[1].split('"')[0]
                )
        for city in cities:
            locs = []
            logger.info("Pulling City %s..." % city)
            r3 = session.get(city, headers=headers)
            if r3.encoding is None:
                r3.encoding = "utf-8"
            for line3 in r3.iter_lines(decode_unicode=True):
                if "View Store Details</a>" in line3:
                    locurl = (
                        "https://oldnavy.gap.com"
                        + line3.split('href="')[1].split('"')[0]
                    )
                    if locurl not in locs:
                        locs.append(locurl)
            for loc in locs:
                logger.info("Pulling Location %s..." % loc)
                website = "oldnavy.com"
                typ = "Old Navy"
                try:
                    store = loc.rsplit("-", 1)[1].replace(".html", "")
                except:
                    store = "<MISSING>"
                hours = ""
                name = ""
                add = ""
                city = ""
                state = ""
                country = "US"
                zc = ""
                phone = ""
                lat = ""
                lng = ""
                if "osagebeach" in loc:
                    name = "PREWITTS POINT"
                    add = "909 Highway D"
                    city = "Osage Beach"
                    state = "MO"
                    zc = "65065"
                    phone = "573-746-2481"
                    lat = "38.161437"
                    lng = "-92.60072"
                    hours = "Mon: 9:00am - 9:00pm; Tue: 9:00am - 9:00pm; Wed: 8:00am - 10:00pm; Thu: Closed; Fri: 12:00am - 11:00pm; Sat: 9:00am - 10:00pm; Sun:10:00am - 8:00pm"
                else:
                    r4 = session.get(loc, headers=headers)
                    lines = r4.iter_lines(decode_unicode=True)
                    for line4 in lines:
                        if 'store_type\\": \\"Outlet\\' in line4:
                            typ = "Old Navy Outlet"
                        if '<div class="location-name"' in line4:
                            name = next(lines).split("<")[0].strip().replace("\t", "")
                        if '"latitude": "' in line4:
                            lat = line4.split('"latitude": "')[1].split('"')[0]
                        if '"longitude": "' in line4:
                            lng = line4.split('"longitude": "')[1].split('"')[0]
                        if '"openingHours": "' in line4:
                            hours = (
                                line4.split('"openingHours": "')[1]
                                .split('"')[0]
                                .strip()
                            )
                        if '"telephone": "' in line4:
                            phone = line4.split('"telephone": "')[1].split('"')[0]
                        if '"streetAddress": "' in line4:
                            add = line4.split('"streetAddress": "')[1].split('"')[0]
                        if '"addressLocality": "' in line4:
                            city = line4.split('"addressLocality": "')[1].split('"')[0]
                        if '"addressRegion": "' in line4:
                            state = line4.split('"addressRegion": "')[1].split('"')[0]
                        if '"postalCode": "' in line4:
                            zc = line4.split('"postalCode": "')[1].split('"')[0]
                if hours == "":
                    hours = "<MISSING>"
                if loc not in alllocs:
                    alllocs.append(loc)
                    name = typ
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
