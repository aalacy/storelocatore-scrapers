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

logger = SgLogSetup().get_logger("fiveguys_com")


def fetch_data():
    locs = [
        "https://restaurants.fiveguys.com/concourse-b-gate-b71-dulles-international-airport"
    ]
    url = "https://restaurants.fiveguys.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "fiveguys.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    Found = True
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "https://restaurants.fiveguys.com/al" in line:
            Found = False
        if (
            "<loc>https://restaurants.fiveguys.com/" in line
            and Found
            and "concourse-b-gate-b71-dulles" not in line
        ):
            locs.append(line.split("<loc>")[1].split("<")[0].replace("&#39;", "'"))
    url = "https://restaurants.fiveguys.ca/sitemap.xml"
    r = session.get(url, headers=headers)
    Found = True
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "https://restaurants.fiveguys.ca/ab</loc>" in line:
            Found = False
        if 'hreflang="en-CA" href="https://restaurants.fiveguys.ca/' in line and Found:
            locs.append(line.split('href="')[1].split('"')[0].replace("&#39;", "'"))
    for loc in locs:
        CS = False
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        if "fiveguys.ca/" in loc:
            country = "CA"
        else:
            country = "US"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "is opening soon" in line2:
                CS = True
            if 'ntityType":"restaurant","id":"' in line2:
                store = line2.split('ntityType":"restaurant","id":"')[1].split('"')[0]
            if name == "" and '<span class="LocationName-geo">' in line2:
                name = line2.split('<span class="LocationName-geo">')[1].split("<")[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                city = line2.split('temprop="addressLocality" content="')[1].split('"')[
                    0
                ]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                dc = 0
                for day in days:
                    if "<!doctype html>" not in day:
                        dc = dc + 1
                        if dc <= 7:
                            hrs = day.split('"')[0]
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if "-" not in phone:
            phone = "<MISSING>"
        if "{: Closed; MONDAY: Closed" in hours:
            hours = "Sun-Sat: Closed"
        hours = hours.replace("</div></div></div></div><div class=;", "").strip()
        name = name.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
        city = city.replace("&#39;", "'")
        if CS is False:
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
