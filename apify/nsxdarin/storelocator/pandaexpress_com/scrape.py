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

logger = SgLogSetup().get_logger("pandaexpress_com")


def fetch_data():
    url = "https://www.pandaexpress.com/locations"
    states = []
    cities = []
    locs = ["https://www.pandaexpress.com/locations/ar/benton/20810-i-30-north"]
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="record" href="/locations/' in line:
            items = line.split('<a class="record" href="/locations/')
            for item in items:
                if 'data-ga-event="locationClick' in item:
                    lurl = (
                        "https://www.pandaexpress.com/locations/" + item.split('"')[0]
                    )
                    states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="record" href="/locations/' in line2:
                items = line2.split('<a class="record" href="/locations/')
                for item in items:
                    if 'data-ga-event="locationClick"' in item:
                        lurl = (
                            "https://www.pandaexpress.com/locations/"
                            + item.split('"')[0]
                        )
                        if "(1) </a>" in item:
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<a href="/locations/' in line2:
                items = line2.split('<a href="/locations/')
                for item in items:
                    if 'data-ga-event="storeDetailsClick"' in item:
                        lurl = (
                            "https://www.pandaexpress.com/locations/"
                            + item.split('"')[0]
                        )
                        locs.append(lurl)
    website = "pandaexpress.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for loc in locs:
        try:
            logger.info(loc)
            hours = ""
            add = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            country = "US"
            store = "<MISSING>"
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '<div class="phone"><a href="tel:' in line2:
                    phone = line2.split('<div class="phone"><a href="tel:')[1].split(
                        '"'
                    )[0]
                if '<link rel="canonical" href="' in line2:
                    purl = line2.split('<link rel="canonical" href="')[1].split('"')[0]
                if '<div class="name"><h2>' in line2:
                    name = (
                        line2.split('<div class="name"><h2>')[1]
                        .split("<")[0]
                        .replace("&amp;", "&")
                    )
                if '<div class="address">' in line2 and add == "":
                    address = line2.split('<div class="address">')[1].split("</div>")[0]
                    add = address.split("<br>")[0].strip()
                    city = address.split("<br>")[1].strip().split(",")[0]
                    state = (
                        address.split("<br>")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .rsplit(" ", 1)[0]
                    )
                    zc = address.strip().rsplit(" ", 1)[1]
                    rawadd = address.replace("<br>", ", ").replace("  ", " ")
                if '<div class="day_name">' in line2:
                    days = line2.split('<div class="day_name">')
                    for day in days:
                        if '<div class="day_hours">' in day:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split('<div class="day_hours">')[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if hours == "":
                hours = "<MISSING>"
            if (
                "," in add
                and "Km " not in add
                and "Lot " not in add
                and "Int. " not in add
                and "Pr2" not in add
                and "Pr-3" not in add
                and "Suite" not in add
            ):
                addnew = add.split(",")[1].strip()
                if len(addnew) <= 2:
                    add = add.replace(",", "")
                else:
                    add = addnew
            if len(zc) >= 5:
                yield SgRecord(
                    locator_domain=website,
                    page_url=purl,
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
                    raw_address=rawadd,
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
