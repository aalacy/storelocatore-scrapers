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

logger = SgLogSetup().get_logger("trotters_co_uk")


def fetch_data():
    locs = []
    url = "https://www.trotters.co.uk/pages/our-stores"
    r = session.get(url, headers=headers)
    website = "trotters.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'Store"><img' in line:
            items = line.split('Store"><img')
            for item in items:
                if 'title="' in item:
                    locs.append(
                        "https://www.trotters.co.uk"
                        + item.split('href="')[1].split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="seo-heading">' in line2:
                name = line2.split('h1 class="seo-heading">')[1].split("<")[0]
            if "Address:<" in line2 and "/trotters-concession-in-harrods" not in loc:
                g = next(lines)
                g = str(g.decode("utf-8"))
                addinfo = g.split("<p>")[1].split("</p>")[0].replace("<br>", "|")
                add = addinfo.split("|")[0]
                city = addinfo.split("|")[1]
                state = "<MISSING>"
                zc = addinfo.split("|")[2]
            if '<a href="tel:' in line2:
                phone = (
                    line2.split('<a href="tel:')[1].split('"')[0].replace("%20", " ")
                )
            if "day</td>" in line2 and "Bank" not in line2:
                hrs = line2.split('">')[1].split("<")[0] + ": "
                g = next(lines)
                g = str(g.decode("utf-8"))
                g = g.replace('uqo3">', 'uqo3"><span>').replace(
                    "<span><span>", "<span>"
                )
                hrs = hrs + g.split("<span>")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "trotters-concession-in-harrods" in loc:
            name = "HARRODS"
            add = "Fourth Floor, Harrods Department Store, 87-135 Brompton Road, Knightsbridge"
            city = "London"
            state = "<MISSING>"
            zc = "SW1X 7XL"
            phone = "<MISSING>"
        if "London" in city:
            city = "London"
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
