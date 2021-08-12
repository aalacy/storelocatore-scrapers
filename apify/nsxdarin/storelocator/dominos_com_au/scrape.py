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

logger = SgLogSetup().get_logger("dominos_com_au")


def fetch_data():
    locs = []
    cities = []
    url = "https://www.dominos.com.au/store-finder"
    r = session.get(url, headers=headers)
    website = "dominos.com.au"
    typ = "<MISSING>"
    country = "AU"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/stores/' in line:
            lurl = (
                "https://www.dominos.com.au" + line.split('<a href="')[1].split('"')[0]
            )
            if lurl.count("/") == 4:
                cities.append(lurl)
    for cname in cities:
        r2 = session.get(cname, headers=headers)
        logger.info(cname)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<a href="/store/' in line2:
                lurl = (
                    "https://www.dominos.com.au/store/"
                    + line2.split('<a href="/store/')[1].split('"')[0]
                )
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        if "test" not in loc:
            r2 = session.get(loc, headers=headers)
            name = ""
            city = ""
            state = loc.split("/store/")[1].split("-")[0].upper()
            zc = ""
            phone = ""
            lat = ""
            lng = ""
            store = loc.rsplit("-", 1)[1]
            hours = ""
            add = ""
            logger.info(loc)
            lines = r2.iter_lines()
            for line2 in lines:
                line2 = str(line2.decode("utf-8"))
                if '<div class="storetitle">' in line2:
                    name = (
                        line2.split('<div class="storetitle">')[1]
                        .split("<")[0]
                        .replace("&#39;", "'")
                    )
                if 'href="http://maps.google.com/maps/search/' in line2:
                    g = next(lines)
                    g = str(g.decode("utf-8")).replace("<Br/>", "<br/>")
                    if "<br/>" not in g:
                        g = next(lines)
                        g = str(g.decode("utf-8")).replace("<Br/>", "<br/>")
                    if "<br/>" not in g:
                        g = next(lines)
                        g = str(g.decode("utf-8")).replace("<Br/>", "<br/>")
                    if "<br/>" not in g:
                        g = next(lines)
                        g = str(g.decode("utf-8")).replace("<Br/>", "<br/>")
                    try:
                        add = (
                            g.rsplit("<br/>", 1)[0]
                            .strip()
                            .replace("\t", "")
                            .replace("<br/>", " ")
                            .replace(",", "")
                        )
                        city = (
                            g.rsplit("<br/>", 1)[0]
                            .rsplit("<br/>", 1)[1]
                            .rsplit(" ", 2)[0]
                        )
                        zc = (
                            g.rsplit("<br/>", 1)[0]
                            .rsplit("<br/>", 1)[1]
                            .rsplit(" ", 1)[1]
                        )
                        state = (
                            g.rsplit("<br/>", 1)[0]
                            .rsplit("<br/>", 1)[1]
                            .rsplit(" ", 2)[1]
                        )
                        add = add.split(city)[0].strip().replace("  ", " ")
                    except:
                        add = "<MISSING>"
                if (
                    '<a href="tel:' in line2
                    and "mobile" not in line2
                    and "click" not in line2
                ):
                    phone = line2.split('<a href="tel:')[1].split('"')[0]
                if 'id="store-lat" value="' in line2:
                    lat = line2.split('id="store-lat" value="')[1].split('"')[0]
                if 'id="store-lon" value="' in line2:
                    lng = line2.split('id="store-lon" value="')[1].split('"')[0]
                if '<span class="visually-hidden">' in line2:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    hrs = (
                        g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if add != "<MISSING>":
                if " (" in add:
                    add = add.split(" (")[0].strip()
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
