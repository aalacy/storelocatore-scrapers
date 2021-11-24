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

logger = SgLogSetup().get_logger("grahamdirect_co_uk")


def fetch_data():
    website = "grahamdirect.co.uk"
    typ = "<MISSING>"
    country = "GB"
    locs = []
    url = "https://www.grahamdirect.co.uk/sitemap/sitemap_branches_graham.xml"
    logger.info("Pulling Stores")
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.grahamdirect.co.uk/branch-finder/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 itemprop="name" class="my-xs-0">' in line2:
                name = line2.split('<h1 itemprop="name" class="my-xs-0">')[1].split(
                    "<"
                )[0]
            if '"streetAddress">' in line2:
                add = (
                    line2.split('"streetAddress">')[1]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = add + g.split(",")[0].strip().replace("\t", "")
            if 'temprop="addressLocality">' in line2:
                city = line2.split('temprop="addressLocality">')[1].split("<")[0]
                state = "<MISSING>"
            if 'temprop="postalCode">' in line2:
                zc = line2.split('temprop="postalCode">')[1].split("<")[0]
            if '"telephone" class="hide">' in line2:
                phone = line2.split('"telephone" class="hide">')[1].split("<")[0]
            if "data-latitude = '" in line2:
                lat = line2.split("data-latitude = '")[1].split("'")[0]
            if "data-longitude = '" in line2:
                lng = line2.split("data-longitude = '")[1].split("'")[0]
            if 'itemprop="openingHours" content="' in line2:
                hrs = line2.split('itemprop="openingHours" content="')[1].split('"')[0]
                if ":" not in hrs:
                    hrs = hrs.replace(" -", ": Closed")
                else:
                    hrs = hrs.replace(" ", ": ")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        store = "<MISSING>"
        add = add.replace(",</span>", "")
        city = city.replace(",", "")
        name = name.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
        city = city.replace("&amp;", "&")
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
