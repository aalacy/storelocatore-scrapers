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

logger = SgLogSetup().get_logger("theburgerspriest_com")


def fetch_data():
    states = []
    cities = []
    locs = []
    url = "https://theburgerspriest.com/find-a-location/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '="Directory-listLink" href="' in line:
            items = line.split('ass="Directory-listLink" href="')
            for item in items:
                if 'a-track="todirectory"' in item:
                    stub = item.split('"')[0]
                    if len(stub) <= 2:
                        states.append(
                            "https://www.theburgerspriest.com/en/locations/" + stub
                        )
                    else:
                        cities.append(
                            "https://www.theburgerspriest.com/en/locations/" + stub
                        )
    for state in states:
        logger.info(state)
        r = session.get(state, headers=headers)
        for line in r.iter_lines():
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        if 'data-count="(1)' in item:
                            locs.append(
                                "https://www.theburgerspriest.com/en/locations/"
                                + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://www.theburgerspriest.com/en/locations/"
                                + item.split('"')[0]
                            )
    for city in cities:
        logger.info(city)
        r = session.get(city, headers=headers)
        for line in r.iter_lines():
            if 'default" href="..' in line:
                items = line.split('default" href="..')
                for item in items:
                    if '">See Details' in item:
                        locs.append(
                            "https://www.theburgerspriest.com/en/locations"
                            + item.split('"')[0]
                        )
    website = "theburgerspriest.com"
    typ = "<MISSING>"
    name = "The Burger's Priest"
    country = "CA"
    store = "<MISSING>"
    hours = ""
    logger.info("Pulling Stores")
    for loc in locs:
        loc = loc.replace("../", "")
        hours = ""
        name = ""
        lat = ""
        lng = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        r = session.get(loc, headers=headers)
        logger.info(loc)
        for line in r.iter_lines():
            if 'aria-current="page">' in line:
                name = line.split('aria-current="page">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line:
                lat = line.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line.split('itemprop="longitude" content="')[1].split('"')[0]
            if '"addressLocality" content="' in line:
                city = line.split('"addressLocality" content="')[1].split('"')[0]
                add = line.split('itemprop="streetAddress" content="')[1].split('"')[0]
                state = line.split('class="c-address-state" itemprop="addressRegion">')[
                    1
                ].split("<")[0]
                zc = line.split('itemprop="postalCode">')[1].split("<")[0]
            if 'data-ya-track="phone">' in line:
                phone = line.split('data-ya-track="phone">')[1].split("<")[0]
            if 'itemprop="openingHours" content="' in line:
                items = line.split('itemprop="openingHours" content="')
                for item in items:
                    if 'lass="c-hours-details-row-day">' in item:
                        hrs = item.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
