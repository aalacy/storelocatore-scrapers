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

logger = SgLogSetup().get_logger("popeyes_com")


def fetch_data():
    locs = []
    states = []
    cities = ["https://locations.popeyes.com/dc/washington"]
    url = "https://locations.popeyes.com/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Directory-listLink" href="' in line:
            items = line.split('"Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    lurl = "https://locations.popeyes.com/" + item.split('"')[0]
                    count = item.split('data-count="(')[1].split(")")[0]
                    if count == 1:
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'ata-count="(' in item:
                        lurl = "https://locations.popeyes.com/" + item.split('"')[0]
                        count = item.split('ata-count="(')[1].split(")")[0]
                        if count == "1":
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Teaser"><a href="..' in line2:
                items = line2.split('"Teaser"><a href="..')
                for item in items:
                    if "Visit Store Website" in item:
                        lurl = "https://locations.popeyes.com" + item.split('"')[0]
                        locs.append(lurl)
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        website = "popeyes.com"
        typ = "<MISSING>"
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        store = ""
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<span class="Hero-subtitle Heading--lead">' in line2:
                name = (
                    line2.split('<span class="Hero-subtitle Heading--lead">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if add == "" and '<meta itemprop="streetAddress" content="' in line2:
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split(
                    '"'
                )[0]
            if 'Address-city">' in line2:
                city = line2.split('Address-city">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
            if 'temprop="latitude" content="' in line2 and lat == "":
                lat = line2.split('temprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('temprop="longitude" content="')[1].split('"')[0]
            if "store-number=" in line2:
                store = line2.split("store-number=")[1].split('"')[0]
            if '"hours":[' in line2 and hours == "":
                days = (
                    line2.split('"hours":[')[1]
                    .split(',"open24HoursMessage"')[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"intervals":' in day:
                        if '"isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('{"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        name = name.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
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
