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

logger = SgLogSetup().get_logger("towerhealth_org")


def fetch_data():
    locs = []
    website = "towerhealth.org"
    country = "US"
    for x in range(0, 151):
        url = "https://towerhealth.org/locations?page=" + str(x)
        r = session.get(url, headers=headers)
        logger.info(str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<h2 class="teaser__name"><a href="' in line:
                lurl = (
                    "https://towerhealth.org"
                    + line.split('<h2 class="teaser__name"><a href="')[1].split('"')[0]
                )
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        typ = "<MISSING>"
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<span class="location-label">' in line2:
                typ = line2.split('<span class="location-label">')[1].split("<")[0]
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '<li class="hours-block__day"><span>' in line2:
                hrs = (
                    line2.split('<li class="hours-block__day"><span>')[1]
                    .split("</li>")[0]
                    .replace("</span>", "")
                    .replace("  ", " ")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if city == "Philadelphia":
            state = "PA"
        name = name.replace("\\u0027", "'")
        if " - " in name:
            name = name.split(" - ")[0]
        if name == "BACA Pediatrics":
            add = "159 North Reading Road"
            zc = "17517"
            city = "Ephrata"
            state = "PA"
        if (
            loc
            == "https://towerhealth.org/locations/st-christophers-pediatric-associates-physical-therapy-e-erie-avenue"
        ):
            zc = "<MISSING>"
        if loc == "https://towerhealth.org/locations/sleep-center":
            city = "Wyomissing"
            zc = "<MISSING>"
        if loc == "https://towerhealth.org/locations/surgical-institute-reading":
            zc = "<MISSING>"
        if loc == "https://towerhealth.org/locations/temple-university-hospital-1":
            zc = "<MISSING>"
        if loc == "https://towerhealth.org/locations/wilmington-va-medical-center":
            zc = "19805"
            city = "Wilmington"
            state = "DE"
        name = name.replace("\\u0026", "&")
        name = name.replace("\\u0027", "'")
        add = add.replace("\\u0026", "&")
        add = add.replace("\\u0027", "'")
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
