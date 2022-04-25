from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("avis_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    sm = "https://www.avis.com/content/dam/avis/na/us/common/seo/all-non-us-locations.xml"
    r = session.get(sm, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.avis.com/en/locations/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 7:
                locs.append(lurl)
    urls = [
        "https://www.avis.com/en/locations/us",
        "https://www.avis.com/en/locations/ca",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if (
                '<a href="/en/locations/us/' in line
                or '<a href="/en/locations/ca/' in line
            ):
                lurl = "https://www.avis.com" + line.split('href="')[1].split('"')[0]
                states.append(lurl)
    for state in states:
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        RFound = False
        for line2 in r2.iter_lines():
            if "<h1>" in line2:
                RFound = True
            if RFound and '<a href="/en/locations/' in line2:
                lurl = "https://www.avis.com" + line2.split('href="')[1].split('"')[0]
                if lurl.count("/") == 8 and "uber-only" not in lurl:
                    locs.append(lurl)
    for loc in locs:
        time.sleep(3)
        LocFound = True
        logger.info("Pulling Location %s..." % loc)
        website = "avis.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        store = loc.rsplit("/", 1)[1]
        city = ""
        add = ""
        state = ""
        zc = ""
        country = ""
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "&amp; Nearby Locations" in line2:
                LocFound = False
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress">' in line2:
                if add == "":
                    add = line2.split('"streetAddress">')[1].split("<")[0].strip()
                else:
                    add = (
                        add
                        + " "
                        + line2.split('"streetAddress">')[1].split("<")[0].strip()
                    )
                    add = add.strip()
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0]
            if '<span class="breadcrumb-view" itemprop="name">' in line2:
                name = line2.split('<span class="breadcrumb-view" itemprop="name">')[
                    1
                ].split("<")[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
            if '"longitude":"' in line2:
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if add == "":
            add = "<MISSING>"
        if zc == "":
            zc = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        phone = phone.replace("\t", "").strip()
        if "Wizard number" in add:
            add = "<MISSING>"
        if add[-1] == ",":
            add = add[:-1]
        if ", (" in add:
            add = add.split(", (")[0]
        if "), " in add:
            add = add.split("), ")[1]
        name = name.replace("&amp;", "&").replace("&quot;", "'")
        if "on/timmins/yts" in loc:
            add = "4599 Airport Rd"
            city = "Timmins"
            state = "ON"
            country = "CA"
            zc = "P4N 7C3"
            name = "Timmins Airport (YTS)"
            phone = "1-705-268-3335"
        name = name.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
        phone = phone.replace("&amp;", "&")
        hours = hours.replace("&amp;", "&")
        loc = loc.replace("&amp;", "&")
        raw_address = add + " " + city + ", " + state + " " + zc + ", " + country
        raw_address = raw_address.strip().replace("  ", " ")
        if LocFound:
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
                raw_address=raw_address,
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
