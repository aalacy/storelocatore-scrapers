from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wexnermedical_osu_edu")


def fetch_data(sgw: SgWriter):
    url = (
        "https://wexnermedical.osu.edu/locations/locations_filter/?name=&service=&care="
    )
    locs = session.get(url, headers=headers).json()
    website = "wexnermedical.osu.edu"
    country = "US"
    logger.info("Pulling Stores")
    found = []
    for i in locs:
        loc = i["Url"]
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        typ = i["Entity"]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2)
            if '<meta property="og:title" content="' in line2:
                name = line2.split('<meta property="og:title" content="')[1].split('"')[
                    0
                ]
            if '<h1 class="globalpagetitle">' in line2:
                name = line2.split('<h1 class="globalpagetitle">')[1].split("<")[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode" : "' in line2:
                zc = line2.split('"postalCode" : "')[1].split('"')[0]
            if '"openingHours": [' in line2:
                hours = (
                    line2.split('"openingHours": [')[1]
                    .split("]")[0]
                    .replace('","', "; ")
                    .replace('"', "")
                )
            if '"telephone": "' in line2:
                phone = (
                    line2.split('"telephone": "')[1]
                    .split('"')[0]
                    .split("or")[0]
                    .strip()
                )
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0]
            if '<span class="phoneLink">' in line2:
                phone = (
                    line2.split('<span class="phoneLink">')[1]
                    .split("<")[0]
                    .split("or")[0]
                    .strip()
                )
        if "Ohio" in name:
            state = "Ohio"
        if len(lat) < 3:
            lat = i["Latitude"]
            lng = i["Longitude"]
        if not hours:
            hours = "Monday: Closed Tuesday: Closed Wednesday: Closed Thursday: Closed Friday: Closed Saturday: Closed Sunday: Closed"
        if not add.strip():
            continue
        if name + add in found:
            continue
        found.append(name + add)

        sgw.write_row(
            SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                store_number=store,
                phone=phone,
                location_type=typ,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
