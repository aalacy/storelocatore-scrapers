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

logger = SgLogSetup().get_logger("ymca_org")


def fetch_data():
    locs = []
    urls = [
        "https://www.ymca.org/sitemap.xml?page=1",
        "https://www.ymca.org/sitemap.xml?page=2",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if "<loc>https://www.ymca.org/locations/" in line:
                locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        r = session.get(loc, headers=headers)
        website = "ymca.org"
        typ = "<MISSING>"
        country = "US"
        hours = ""
        logger.info(loc)
        for line in r.iter_lines():
            if '"shortlink" href="https://www.ymca.org/node/' in line:
                store = line.split('"shortlink" href="https://www.ymca.org/node/')[
                    1
                ].split('"')[0]
            if '"og:title" content="' in line:
                name = line.split('"og:title" content="')[1].split('"')[0]
            if 'data-lat="' in line:
                lat = line.split('data-lat="')[1].split('"')[0]
                lng = line.split('data-lng="')[1].split('"')[0]
            if '<span class="address-line1">' in line:
                add = line.split('<span class="address-line1">')[1].split("<")[0]
            if 'class="locality">' in line:
                city = line.split('class="locality">')[1].split("<")[0]
            if '<span class="administrative-area">' in line:
                state = line.split('<span class="administrative-area">')[1].split("<")[
                    0
                ]
            if '<span class="postal-code">' in line:
                zc = line.split('<span class="postal-code">')[1].split("<")[0]
            if '><a href="tel:' in line:
                phone = line.split('><a href="tel:')[1].split('"')[0].replace("+", "")
            if ":</td>" in line:
                hrs = line.split("<td>")[1].split("<")[0]
            if "m</td>" in line:
                hrs = hrs + " " + line.split("<td>")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
