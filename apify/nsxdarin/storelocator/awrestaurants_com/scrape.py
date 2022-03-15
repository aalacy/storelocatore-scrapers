from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("awrestaurants_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://awrestaurants.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>http://awdev.dev.wwbtc.com/locations/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(
                lurl.replace(
                    "awdev.dev.wwbtc.com/locations", "awrestaurants.com/locations"
                )
            )
    for loc in locs:
        Closed = False
        logger.info(("Pulling Location %s..." % loc))
        website = "awrestaurants.com"
        typ = "Restaurant"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        country = "US"
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<div class="hours__row">' in line2:
                g = next(lines)
                while "</div>" not in g:
                    g = next(lines)
                    if "00" in g or "30" in g or "am-" in g or "am -" in g:
                        if "-->" not in g:
                            hrs = (
                                g.strip()
                                .replace("\r", "")
                                .replace("\t", "")
                                .replace("\n", "")
                                .replace("&nbsp;", " ")
                            )
                            if ">" in hrs:
                                hrs = hrs.split(">")[1].split("<")[0]
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if 'main-name"><h1>' in line2:
                name = line2.split('main-name"><h1>')[1].split("<")[0]
            if '"store":{"address":"' in line2:
                add = line2.split('"store":{"address":"')[1].split('"')[0]
                city = line2.split(',"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"long":"')[1].split('"')[0]
                try:
                    phone = line2.split(',"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
            if "This location is temporarily closed" in line2:
                Closed = True
        if hours == "":
            hours = "<MISSING>"
        if Closed:
            hours = "Temporarily Closed"
        if add != "":
            add = add.replace("\\u0026", "&")
            name = name.replace("\\u0026", "&")
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
