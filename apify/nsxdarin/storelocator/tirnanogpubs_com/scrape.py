from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()

logger = SgLogSetup().get_logger("tirnanogpubs_com")


def fetch_data():
    website = "tirnanogpubs.com"
    typ = "<MISSING>"
    country = "CA"
    locs = []
    logger.info("Pulling Stores")
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }
    sid = ""
    url = "https://www.tirnanogpubs.com/en/locations.html"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-ya-track="todirectory"' in item:
                    lurl = (
                        "https://www.tirnanogpubs.com/en/locations/"
                        + item.split('"')[0]
                    )
                    locs.append(lurl)
    for loc in locs:
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
            if '"c-bread-crumbs-name" itemprop="name">' in line2 and name == "":
                name = line2.rsplit('"c-bread-crumbs-name" itemprop="name">', 1)[
                    1
                ].split("<")[0]
            if '<meta itemprop="streetAddress" content="' in line2:
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split(
                    '"'
                )[0]
                city = line2.split('"c-address-city">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if '"Phone-link" href="tel:' in line2:
                phone = line2.split('"Phone-link" href="tel:')[1].split('"')[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<td class="c-hours-details-row-day">' in day:
                        hrs = day.split('"')[0]
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
