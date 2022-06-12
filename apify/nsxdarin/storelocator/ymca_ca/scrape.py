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

logger = SgLogSetup().get_logger("ymca_ca")


def fetch_data():
    url = "https://www.ymca.ca/locations?type=ymca,camps&amenities"
    r = session.get(url, headers=headers)
    website = "ymca.ca"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    coords = []
    for line in lines:
        if '"lat":' in line:
            items = line.split('"lat":')
            for item in items:
                if '"lng":' in item:
                    ll = (
                        item.split(",")[0]
                        + "|"
                        + item.split('"lng":')[1].split(",")[0]
                        + "|"
                        + item.split('"name":"')[1].split('"')[0]
                    )
                    coords.append(ll)
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if 'class="btn-primary" aria-label="' in line:
            loc = "https://www.ymca.ca" + line.split('href="')[1].split('"')[0]
        if 'class="title-link text-primary" rel="bookmark">' in line:
            next(lines)
            name = next(lines).split("<span>")[1].split("<")[0]
            for coord in coords:
                if coord.split("|")[2] == name:
                    lat = coord.split("|")[0]
                    lng = coord.split("|")[1]
        if '<i class="fas fa-map-marker-alt text-gray-300"></i>' in line:
            add = next(lines).split("<")[0].strip().replace("\t", "")
            csz = (
                next(lines)
                .strip()
                .replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
            )
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.split(",")[1].strip().split(" ")[1] + " " + csz.rsplit(" ", 1)[1]
        if '<a href="tel:' in line and loc != "<MISSING>":
            phone = (
                line.split('<a href="tel:')[1]
                .split('"')[0]
                .replace("%28", "(")
                .replace("%29", ")")
            )
            if "ull" in phone:
                phone = "<MISSING>"
            name = name.replace("&#039;", "'")
            add = add.replace("&#039;", "'")
            city = city.replace("&#039;", "'")
            if "2-301" in add:
                phone = "587-537-5000"
            if "B4H3B2" in zc:
                zc = "B4H3B2"
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
