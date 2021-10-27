from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("northwesternmutual_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.northwesternmutual.com/office/sitemap-office-pages.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.northwesternmutual.com/office/" in line:
            items = line.split("<loc>https://www.northwesternmutual.com/office/")
            for item in items:
                if "xml version=" not in item:
                    lurl = (
                        "https://www.northwesternmutual.com/office/"
                        + item.split("<")[0]
                    )
                    if (
                        lurl.count("/") == 7
                        and "giving-back" not in lurl
                        and "advisor-team" not in lurl
                    ):
                        locs.append(lurl)
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "northwesternmutual.com"
        typ = "Financial Advisor"
        hours = "<MISSING>"
        add = ""
        city = ""
        phone = ""
        state = ""
        country = "US"
        zc = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        try:
            r2 = session.get(loc, headers=headers)
            logger.info(f"Response Status Code:{r2.status_code}")
            if r2.status_code != 200:
                continue
            for line2 in r2.iter_lines():
                if '<p class="nmxo-utility-nav--text">' in line2:
                    name = (
                        line2.split('<p class="nmxo-utility-nav--text">')[1]
                        .split("<")[0]
                        .strip()
                    )
                if '"streetAddress": "' in line2:
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if '"addressLocality": "' in line2:
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                if '"addressRegion": "' in line2:
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                if '"telePhone": "' in line2:
                    phone = line2.split('"telePhone": "')[1].split('"')[0]
                if '"openingHours": "' in line2:
                    hours = line2.split('"openingHours": "')[1].split('"')[0]
                if '"latitude": "' in line2:
                    lat = line2.split('"latitude": "')[1].split('"')[0]
                if '"longitude": "' in line2:
                    lng = line2.split('"longitude": "')[1].split('"')[0]
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
