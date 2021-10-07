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

logger = SgLogSetup().get_logger("chuckecheese_com")


def fetch_data():
    locs = []
    cities = []
    states = []
    website = "chuckecheese.com"
    typ = "<MISSING>"
    countries = [
        "https://locations.chuckecheese.com/ca",
        "https://locations.chuckecheese.com/pr",
        "https://locations.chuckecheese.com/us",
    ]
    logger.info("Pulling Stores")
    for cty in countries:
        r = session.get(cty, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"Directory-listLink" href="' in line:
                items = line.split('"Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="directorylink"' in item:
                        purl = (
                            "https://locations.chuckecheese.com/" + item.split('"')[0]
                        )
                        if purl.count("/") == 6:
                            locs.append(purl)
                        else:
                            states.append(purl)
    for surl in states:
        logger.info(surl)
        r = session.get(surl, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"Directory-listLink" href="../' in line:
                items = line.split('"Directory-listLink" href="../')
                for item in items:
                    if 'data-ya-track="directorylink"' in item:
                        purl = (
                            "https://locations.chuckecheese.com/" + item.split('"')[0]
                        )
                        if purl.count("/") == 6:
                            locs.append(purl)
                        else:
                            cities.append(purl)
    for curl in cities:
        logger.info(curl)
        r = session.get(curl, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<a class="Teaser-link" href="../../' in line:
                items = line.split('<a class="Teaser-link" href="../../')
                for item in items:
                    if 'data-ya-track="visitpage">View' in item:
                        purl = (
                            "https://locations.chuckecheese.com/" + item.split('"')[0]
                        )
                        locs.append(purl)
    for loc in locs:
        logger.info(loc)
        loc = loc.replace("&amp;", "&").replace("&#39;", "'")
        if (
            "https://locations.chuckecheese.com/us" in loc
            or "https://locations.chuckecheese.com/pr" in loc
        ):
            country = "US"
        else:
            country = "CA"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "(count = 1)', '" in line2:
                name = line2.split("(count = 1)', '")[1].split("'")[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                zc = line2.split('temprop="postalCode">')[1].split("<")[0]
                city = line2.split('><span class="c-address-city">')[1].split("<")[0]
                if "/pr/" not in loc:
                    state = line2.split('<span class="c-address-state" >')[1].split(
                        "<"
                    )[0]
                else:
                    state = "PR"
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                dc = 0
                for day in days:
                    if '<link id="page-url"' not in day:
                        dc = dc + 1
                        hrs = day.split('"')[0]
                        if dc <= 7:
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
        name = name.replace("&#39;", "'").replace("&amp;", "&")
        add = add.replace("&#39;", "'").replace("&amp;", "&")
        city = city.replace("&#39;", "'").replace("&amp;", "&")
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
