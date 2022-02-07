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

logger = SgLogSetup().get_logger("easterndental_com")


def fetch_data():
    url = "https://www.easterndental.com/locations/"
    r = session.get(url, headers=headers)
    website = "easterndental.com"
    locs = []
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            '<div class="fwpl-item el-i1ybmv button smallest"><a href="https://www.easterndental.com/locations/'
            in line
        ):
            items = line.split(
                '<div class="fwpl-item el-i1ybmv button smallest"><a href="https://www.easterndental.com/locations/'
            )
            for item in items:
                if '<div class="facetwp-template" data-name="locations">' not in item:
                    locs.append(
                        "https://www.easterndental.com/locations/" + item.split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        hours = ""
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<div class="marker" data-lat="' in line:
                lat = line.split('<div class="marker" data-lat="')[1].split('"')[0]
                lng = line.split('data-lng="')[1].split('"')[0]
                g = next(lines)
                add = g.split(">")[1].split("<")[0]
                g = next(lines)
                if "," in g:
                    city = g.split(",")[0].strip().replace("\t", "")
                    state = g.split(",")[1].strip().split(" ")[0]
                    zc = g.split("<")[0].rsplit(" ", 1)[1]
                else:
                    add = add + " " + g.split("<")[0].strip().replace("\t", "")
                    g = next(lines)
                    city = g.split(",")[0].strip().replace("\t", "")
                    state = g.split(",")[1].strip().split(" ")[0]
                    zc = g.split("<")[0].rsplit(" ", 1)[1]
            if "Phone: </strong>" in line:
                phone = (
                    line.split("Phone: </strong>")[1]
                    .split("<")[0]
                    .strip()
                    .replace("\t", "")
                )
            if "<title>" in line:
                name = line.split("<title>")[1].split("<")[0]
            if "day</div>" in line:
                day = line.split(">")[1].split("<")[0].strip()
                g = next(lines)
                g = next(lines)
                if "<div>" in g:
                    hrs = (
                        day
                        + ": "
                        + g.split(">")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                    g = next(lines)
                    if "0" in g:
                        hrs = hrs + "-" + g.split("<")[0].strip().replace("\t", "")
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                    hours = hours.replace("*", "").replace("--", "-")
        name = name.replace(" - Eastern Dental", "")
        hours = hours.replace("- ", "-").replace("- ", "-")
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
