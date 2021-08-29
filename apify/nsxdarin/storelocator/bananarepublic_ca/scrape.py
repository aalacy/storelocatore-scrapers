from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("bananarepublic_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    cities = []
    url = "https://bananarepublic.gapcanada.ca/stores/"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'class="ga-link" data-ga="Maplist, Region ' in line:
            stub = line.split('href="')[1].split('"')[0]
            lurl = "https://bananarepublic.gapcanada.ca/" + stub
            if lurl not in states:
                states.append(lurl)
    for state in states:
        if "/" in state:
            logger.info(("Pulling Province %s..." % state))
            r2 = session.get(state, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'data-city-item="' in line2:
                    lurl = (
                        "https://bananarepublic.gapcanada.ca/"
                        + line2.split('href="')[1].split('"')[0]
                    )
                    if lurl not in cities:
                        cities.append(lurl)
    for city in cities:
        logger.info(("Pulling City %s..." % city))
        r2 = session.get(city, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a class="view-store ga-link"' in line2:
                lurl = (
                    "https://bananarepublic.gapcanada.ca/"
                    + line2.split('href="')[1].split('"')[0]
                )
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        loc = loc.replace("ca//stores", "ca/stores")
        logger.info("Pulling Location %s..." % loc)
        website = "bananarepublic.ca"
        typ = ""
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        Outlet = False
        zc = ""
        country = "CA"
        store = ""
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if 'class="daypart" data-daypart="' in line2:
                day = line2.split('data-daypart="')[1].split('"')[0]
                next(lines)
                next(lines)
                next(lines)
                hrs = day + ": " + next(lines).split(">")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '{"docEl":null' in line2:
                store = line2.split('"lid":')[1].split(",")[0]
                name = line2.split('location_name\\":\\"')[1].split("\\")[0]
                city = line2.split('"city\\":\\"')[1].split("\\")[0]
                lat = line2.split('"lat":')[1].split(",")[0]
                lng = line2.split('"lng":')[1].split(",")[0]
                try:
                    add = (
                        line2.split('"address_1\\":\\"')[1].split("\\")[0]
                        + " "
                        + line2.split('"address_2":"')[1].split("\\")[0]
                    )
                    add = add.strip()
                except:
                    add = line2.split('"address_1\\":\\"')[1].split("\\")[0]
                state = line2.split('"region\\":\\"')[1].split("\\")[0]
                zc = line2.split('"post_code\\":\\"')[1].split("\\")[0]
                phone = line2.split('"local_phone\\":\\"')[1].split("\\")[0]
                typ = line2.split('"store_type\\": \\"')[1].split("\\")[0]
            if 'spid5":{"name":"Factory Store' in line2:
                Outlet = True
        if typ == "":
            typ = "Store"
        if Outlet:
            name = "Banana Republic Outlet"
        else:
            name = "Banana Republic"
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
