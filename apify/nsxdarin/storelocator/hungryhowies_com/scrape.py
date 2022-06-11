from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("hungryhowies_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    for x in range(0, 101):
        logger.info("Pulling Page %s..." % str(x))
        url = "https://www.hungryhowies.com/locations?page=" + str(x)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<div class="details roundButton"><a href="/store/' in line:
                lurl = (
                    "https://www.hungryhowies.com"
                    + line.split('href="')[1].split('"')[0]
                )
                locs.append(lurl)
            if '<div class="details roundButton"><a href="/STORE/' in line:
                lurl = (
                    "https://www.hungryhowies.com"
                    + line.split('href="')[1].split('"')[0]
                )
                locs.append(lurl)
        logger.info("Found %s Locations..." % str(len(locs)))
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        country = "US"
        website = "hungryhowies.com"
        typ = "Restaurant"
        hours = ""
        for line2 in lines:
            if '<h1 class="title" id="page-title">' in line2:
                name = line2.split('<h1 class="title" id="page-title">')[1].split("<")[
                    0
                ]
                name = name.replace("&#039;", "'")
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split(',"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split(',"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '<dt class="day">' in line2:
                items = line2.split('<dt class="day">')
                for item in items:
                    if '<dd class="time">' in item:
                        if hours == "":
                            hours = (
                                item.split("<")[0]
                                + " "
                                + item.split('<dd class="time">')[1].split("<")[0]
                            )
                        else:
                            hours = (
                                hours
                                + "; "
                                + item.split("<")[0]
                                + " "
                                + item.split('<dd class="time">')[1].split("<")[0]
                            )
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        store = name.rsplit("#", 1)[1]
        if len(phone) < 3:
            phone = "<MISSING>"
        if "5555 Con" in add:
            phone = "<MISSING>"
        if "0000000" in phone:
            name = name + " - Coming Soon"
        if phone == "0000000000":
            phone = "<MISSING>"
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
