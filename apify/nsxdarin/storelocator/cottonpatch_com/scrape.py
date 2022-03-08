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

logger = SgLogSetup().get_logger("cottonpatch_com")


def fetch_data():
    locs = []
    url = "https://cottonpatch.com/locations/"
    r = session.get(url, headers=headers)
    website = "cottonpatch.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            'href="https://cottonpatch.com/locations/' in line
            and "cta-button" not in line
            and 'class="title">' not in line
        ):
            lurl = line.split('href="')[1].split('"')[0]
            if lurl != "https://cottonpatch.com/locations/":
                locs.append(lurl)
    for loc in locs:
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
        HFound = False
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace("&#8211;", "-")
            if add == "" and 'class="contact-group">' in line2:
                g = next(lines)
                add = g.split("<p>")[1].split("<")[0]
                g = next(lines)
                city = g.split(",")[0].strip().replace("\t", "")
                state = g.split(",")[1].strip().split(" ")[0]
                zc = g.split("<")[0].rsplit(" ", 1)[1]
                g = next(lines)
                phone = (
                    g.split("<")[0]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
            if lat == "" and "other_coords=[{lat:" in line2:
                lat = line2.split("other_coords=[{lat:")[1].split(",")[0]
                lng = line2.split("lng:")[1].split("}")[0]
            if '<div class="hours-group">' in line2 and hours == "":
                HFound = True
            if HFound and ">Menu</a>" in line2:
                HFound = False
            if HFound and "pm<" in line2:
                hrs = line2.replace("<p>", "").split("<")[0].strip()
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "locations/corsicana" in loc:
            phone = "903-874-2020"
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
