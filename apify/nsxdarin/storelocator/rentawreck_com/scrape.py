import csv
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

logger = SgLogSetup().get_logger("rentawreck_com")

def fetch_data():
    locs = [
        "https://www.rentawreck.com/car-rental-los-angeles-CA.htm|1|33.9954109192|-118.4385604858"
    ]
    url = "https://www.rentawreck.com/locations.htm"
    r = session.get(url, headers=headers)
    website = "rentawreck.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<li class="locON state_US state_' in line:
            items = line.split('<li class="locON state_US state_')
            for item in items:
                if 'varangerbotn/"' not in item:
                    llat = item.split('data-lat="')[1].split('"')[0]
                    llng = item.split('data-lon="')[1].split('"')[0]
                    sid = item.split('data-id="')[1].split('"')[0]
                    lurl = item.split('data-uri="')[1].split('"')[0]
                    if "gillette-wy" not in lurl:
                        locs.append(
                            "https://www.rentawreck.com"
                            + lurl
                            + "|"
                            + sid
                            + "|"
                            + llat
                            + "|"
                            + llng
                        )
    for loc in locs:
        purl = loc.split("|")[0]
        logger.info(purl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("|")[1]
        phone = ""
        lat = loc.split("|")[2]
        lng = loc.split("|")[3]
        hours = ""
        r2 = session.get(purl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if name == "" and 'data-name="' in line2:
                name = line2.split('data-name="')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '"dayOfWeek":["' in line2:
                days = line2.split('"dayOfWeek":["')
                for day in days:
                    if '"closes":"' in day:
                        if '"closes":"Closed"' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"opens":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closes":"')[1].split('"')[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if "heap-car-rental-haltom-city-TX.htm" in purl:
            name = "Rent-A-Wreck of Haltom City"
            state = "TX"
            city = "Haltom City"
            add = "5521 Denton Highway"
            zc = "76148"
            phone = "(817) 507-3707"
            hours = "Mon-Fri: 8:00AM - 5:00PM; Sat-Sun: Closed"
        if "cheap-car-rental-rockville-MD.htm" in purl:
            name = "Rent-A-Wreck of Rockville"
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
            hours_of_operation=hours,
        )
    name = "Rent-A-Wreck Of Gillette (GCC)"
    purl = "https://www.pricelesscarrental.com/car-rental-gillette-wy.htm"
    add = "513 E. 2nd St"
    city = "Gillette"
    state = "WY"
    zc = "82716"
    phone = "(307) 363-4388"
    store = "145"
    hours = "Mon-Fri: 9:00AM-6:00PM; Sat: 9:00AM-5:00PM; Sun: Closed"
    lat = "44.2932434082"
    lng = "-105.4979171753"
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
        hours_of_operation=hours,
    )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
