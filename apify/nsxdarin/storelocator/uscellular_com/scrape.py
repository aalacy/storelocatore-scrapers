from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("uscellular_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    sm = "https://local.uscellular.com/sitemap.xml"
    r = session.get(sm, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "sitemap.xml" in line:
            states.append(
                line.strip().replace("\r", "").replace("\t", "").replace("\n", "")
            )
    for state in states:
        r2 = session.get(state, headers=headers)
        logger.info(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "https://local.uscellular.com/" in line2:
                locs.append(
                    line2.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                )
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "uscellular.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        store = "<MISSING>"
        state = ""
        zc = ""
        country = "US"
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<strong class="name">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                name = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
            if '<div class="street">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
            if '<div class="locality">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                csz = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().split(" ")[0]
                zc = csz.rsplit(" ", 1)[1]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if 'class="location-detail-phone-number">' in line2:
                phone = line2.split("tel:")[1].split('"')[0]
            if '"openingHours":["' in line2:
                hours = (
                    line2.split('"openingHours":["')[1]
                    .split("]")[0]
                    .replace('","', "; ")
                    .replace('"', "")
                )
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "a href" not in name:
            name = name.replace("&amp;", "&")
            add = add.replace("&amp;", "&")
            hours = hours.replace("&amp;", "&")
            phone = phone.replace("&amp;", "&")
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
