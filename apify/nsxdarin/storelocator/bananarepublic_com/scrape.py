from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("bananarepublic_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    stnames = []
    states = []
    url = "https://bananarepublic.gap.com/stores/"
    website = "bananarepublic.com"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line)
        if '<a href="/stores/' in line:
            stname = line.split('<a href="/stores/')[1].split('"')[0]
            if stname not in stnames:
                stnames.append(stname)
                states.append("https://bananarepublic.gap.com/stores/" + stname)
    for state in states:
        cities = []
        logger.info("Pulling State %s..." % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2)
            if '<a href="/stores/' in line2:
                cities.append(
                    "https://bananarepublic.gap.com"
                    + line2.split('href="')[1].split('"')[0]
                )
        for city in cities:
            locs = []
            logger.info("Pulling City %s..." % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                line3 = str(line3)
                if "View Store Details</a>" in line3:
                    locs.append(
                        "https://bananarepublic.gap.com"
                        + line3.split('href="')[1].split('"')[0]
                    )
            for loc in locs:
                logger.info("Pulling Location %s..." % loc)
                Outlet = False
                website = "bananarepublic.com"
                typ = "<MISSING>"
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
                r4 = session.get(loc, headers=headers)
                lines = r4.iter_lines()
                for line4 in lines:
                    line4 = str(line4)
                    if '<div class="location-name"' in line4:
                        g = next(lines)
                        g = str(g)
                        name = g.split("<")[0].strip().replace("\t", "")
                    if '"latitude": "' in line4:
                        lat = line4.split('"latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line4:
                        lng = line4.split('"longitude": "')[1].split('"')[0]
                    if '"openingHours": "' in line4:
                        hours = (
                            line4.split('"openingHours": "')[1].split('"')[0].strip()
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
                    if '{"spid5":{"name":"Factory Store"' in line4:
                        Outlet = True
                if hours == "":
                    hours = "<MISSING>"
                name = "Banana Republic"
                if Outlet:
                    name = "Banana Republic Outlet"
                if name != "" and ".html" in loc:
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
