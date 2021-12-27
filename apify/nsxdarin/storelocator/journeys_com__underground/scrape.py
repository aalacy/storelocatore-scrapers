from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("journeys_com__underground")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.journeys.com/underground"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'class="link-store-info btn-action">' in line:
            locs.append(
                "https://www.journeys.com" + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        AFound = False
        lines = r2.iter_lines(decode_unicode=True)
        website = "journeys.com/underground"
        add = ""
        hours = ""
        for line2 in lines:
            if '<p itemprop="streetAddress">' in line2:
                AFound = True
            if AFound and '<span itemprop="addressLocality">' in line2:
                website = "journeys.com"
                AFound = False
                city = line2.split('span itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
                country = "US"
            if AFound and "<p item" not in line2 and "</p>" in line2 and "<p>" in line2:
                add = add + " " + line2.split("<p>")[1].split("<")[0]
            if '<h2 itemprop="name">' in line2:
                name = line2.split('<h2 itemprop="name">')[1].split("<")[0].strip()
                try:
                    store = name.split("#")[1]
                except:
                    store = "<MISSING>"
                typ = name.split("#")[0].title().strip()
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
            if '<span itemprop="openingHours"' in line2:
                hrs = (
                    line2.split('<span itemprop="openingHours"')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "</html>" in line2:
                lat = "<MISSING>"
                lng = "<MISSING>"
        add = add.strip()
        if add == "":
            add = "<MISSING>"
        name = typ
        if "journeys-458-fulton-street" in loc:
            add = "458 Fulton Street"
        if "journeys-236-powell-street" in loc:
            add = "236 Powell Street"
        if "journeys-133-s-state-st" in loc:
            add = "133 S State St"
        if "journeys-626-broadway" in loc:
            add = "626 Broadway"
        if "journeys-34-w-34th-street" in loc:
            add = "34 W 34th Street"
        if "journeys-42b-w-14th-st" in loc:
            add = "42B W 14th St"
        name = "Underground by Journeys"
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
