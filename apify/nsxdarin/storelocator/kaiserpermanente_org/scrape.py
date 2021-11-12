from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("kaiserpermanente_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    urls = [
        "https://healthy.kaiserpermanente.org/northern-california/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/southern-california/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/colorado-denver-boulder-mountain-northern/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/southern-colorado/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/georgia/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/hawaii/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/maryland-virginia-washington-dc/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/oregon-washington/facilities/sitemap",
        "https://healthy.kaiserpermanente.org/washington/facilities/sitemap",
    ]
    for url in urls:
        logger.info(url)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if "<loc>https://healthy.kaiserpermanente.org/" in line:
                items = line.split("<loc>https://healthy.kaiserpermanente.org/")
                for item in items:
                    if "<?xml" not in item:
                        lurl = (
                            "https://healthy.kaiserpermanente.org/" + item.split("<")[0]
                        )
                        locs.append(lurl)
    logger.info(("Found %s Locations..." % str(len(locs))))
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "kaiserpermanente.org"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        store = loc.rsplit("-", 1)[1]
        lat = ""
        lng = ""
        zc = ""
        phone = ""
        r2 = session.get(loc, headers=headers)
        try:
            lines = r2.iter_lines()
            AF = False
            for line2 in lines:
                if "Affiliated facility" in line2:
                    AF = True
                if (
                    'phone-number styling-5-marketing" x-ms-format-detection="none">'
                    in line2
                ):
                    g = next(lines)
                    phone = (
                        g.strip().replace("\t", "").replace("\r", "").replace("\t", "")
                    )
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0]
                    if " |" in name:
                        name = name.split(" |")[0]
                if '{"street":"' in line2 and add == "":
                    add = line2.split('{"street":"')[1].split('"')[0]
                    city = line2.split('"city":"')[1].split('"')[0]
                    state = line2.split('"state":"')[1].split('"')[0]
                    zc = line2.split('"zip":"')[1].split('"')[0]
                    try:
                        lat = line2.split('"lat":"')[1].split('"')[0]
                        lng = line2.split('"lng":"')[1].split('"')[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    if ", Suite" in add:
                        add = add.split(", Suite")[0]
                    if " Suite" in add:
                        add = add.split(" Suite")[0]
                    if ", Ste" in add:
                        add = add.split(", Ste")[0]
                    if " Ste" in add:
                        add = add.split(" Ste")[0]
                if '<ul class="fd--no-bullets fd--no-padding-margin">' in line2:
                    g = next(lines)
                    hours = g.split(">")[1].split("<")[0]
                    next(lines)
                    g = next(lines)
                    if "day" in g and "<li>" in g:
                        hours = hours + "; " + g.split(">")[1].split("<")[0].strip()
                if "> Holidays" in line2:
                    hours = hours + "; " + line2.split(">")[1].split("<")[0].strip()
            if hours == "":
                hours = "<MISSING>"
            if "day" not in hours and "MISSING" not in hours:
                hours = hours + " - 7 days"
            if ", Located" in add:
                add = add.split(", Located")[0].strip()
            if (
                "https://healthy.kaiserpermanente.org/georgia/facilities/Kaiser-Permanente-Gwinnett-Comprehensive-Medical-Center-100464"
                in loc
            ):
                add = "3650 Steve Reynolds Blvd"
            if "Steele-Street-Medical-Center-339023" in loc:
                add = "505 Steele St S"
            if AF is False:
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
