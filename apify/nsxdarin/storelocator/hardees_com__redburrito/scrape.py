from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("hardees_com__redburrito")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://hardees.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "hardees.com"
    for line in r.iter_lines():
        if "<loc>https://locations.hardees.com/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0].replace("--", "-"))
    for loc in locs:
        try:
            if "fort-smith/1820-phoenix" in loc:
                loc = "https://locations.hardees.com/ar/fort-smith/1820-phoenix-ave"
            logger.info(loc)
            country = "US"
            typ = "<MISSING>"
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            lat = ""
            store = "<MISSING>"
            lng = ""
            hours = ""
            RB = False
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0]
                    if ":" in name:
                        name = name.split(":")[0].strip()
                if '"dimension4":"' in line2:
                    add = line2.split('"dimension4":"')[1].split('"')[0]
                if '"Address-field Address-city">' in line2:
                    city = line2.split('"Address-field Address-city">')[1].split("<")[0]
                if 'itemprop="addressRegion">' in line2:
                    state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                if 'itemprop="postalCode">' in line2:
                    zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                if '<a href="tel:' in line2:
                    phone = line2.split('<a href="tel:')[1].split('"')[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split(
                        '"'
                    )[0]
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split(
                        '"'
                    )[0]
                if hours == "" and '"highlightTodayBackground":null,"hours":[' in line2:
                    days = (
                        line2.split('"highlightTodayBackground":null,"hours":[')[1]
                        .split('],"open24HoursMessage":')[0]
                        .split('"day":"')
                    )
                    for day in days:
                        if '"intervals"' in day:
                            if '"isClosed":false' not in day:
                                hrs = day.split('"')[0] + ": Closed"
                            else:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split('"start":')[1].split("}")[0]
                                    + "-"
                                    + day.split('"end":')[1].split(",")[0]
                                )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                if "Red Burrito</span>" in line2:
                    RB = True
            if RB is True:
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
