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

logger = SgLogSetup().get_logger("crackerbarrel_com")


def fetch_data():
    locs = []
    url = "https://www.crackerbarrel.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "crackerbarrel.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://crackerbarrel.com/Locations/States/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 7:
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"address1":"' in line2:
                add = line2.split('"address1":"')[1].split('"')[0]
            if '"city":"' in line2:
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                name = "Cracker Barrel in " + city + ", " + state
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('latitude":"')[1].split('"')[0]
                lng = line2.split('longitude":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                hours = (
                    "Sun: "
                    + line2.split('"Sunday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Sunday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Monday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Monday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Tuesday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Tuesday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Wednesday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Wednesday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Thursday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Thursday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Friday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Friday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Saturday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Saturday_Close":{"value":"')[1].split('"')[0]
                )
        if "States/ga/lavonia/750" in loc:
            name = "Cracker Barrel in Lavonia"
            city = "Lavonia"
            state = "GA"
            add = "725 Ross Place"
            zc = "30553"
            phone = "706-356-1255"
            hours = "Sun-Thu: 7:00 AM - 9:00 PM; Fri-Sat: 7:00 AM - 10:00 PM"
            lat = "34.444933"
            lng = "-83.1243957"
        if "States/ky/middlesboro/706" in loc:
            name = "Cracker Barrel in Middlesboro"
            city = "Middlesboro"
            state = "KY"
            zc = "40965"
            add = "1049 N.12th St."
            phone = "606-248-7011"
            hours = "Sun-Thu: 7:00 AM - 9:00 PM; Fri-Sat: 7:00 AM - 10:00 PM"
            lat = "36.614289"
            lng = "-83.7017957"
        if "States/ar/conway/276" in loc:
            name = "Cracker Barrel in Conway"
            city = "Conway"
            state = "AR"
            zc = "72032"
            add = "525 Skyline Drive"
            phone = "501-327-6107"
            hours = "Sun-Thu: 7:00 AM - 9:00 PM; Fri-Sat: 7:00 AM - 10:00 PM"
            lat = "35.1107489"
            lng = "-92.4319122"
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
