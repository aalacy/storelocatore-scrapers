from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("allbirds_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = [
        "https://stores.allbirds.com/location/paris-le-bon-marche",
        "https://stores.allbirds.com/location/paris-galeries-lafayette-haussmann",
    ]
    url = "https://stores.allbirds.com/"
    r = session.get(url, headers=headers)
    website = "allbirds.com"
    store = "<MISSING>"
    typ = "Store"
    name = ""
    for line in r.iter_lines():
        if '<a href="/location/' in line:
            items = line.split('<a href="/location/')
            for item in items:
                if '<p class="text-lg ">' in item:
                    lurl = "https://stores.allbirds.com/location/" + item.split('"')[0]
                    locs.append(lurl)
    for loc in locs:
        r = session.get(loc, headers=headers)
        logger.info(loc)
        add = ""
        city = ""
        state = ""
        zc = ""
        country = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        for line in r.iter_lines():
            if '"addressCountry": "' in line:
                country = line.split('"addressCountry": "')[1].split('"')[0]
            if '"streetAddress": "' in line:
                add = line.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line:
                city = line.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line:
                state = line.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = (
                    line.split('"longitude": ')[1]
                    .strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                )
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"telephone": "' in line:
                phone = line.split('"telephone": "')[1].split('"')[0]
            if '<div class="storeHours"><p class="leading-6">' in line:
                hours = (
                    line.split('<div class="storeHours"><p class="leading-6">')[1]
                    .split("</div>")[0]
                    .replace('</p><p class="leading-6">', "; ")
                    .replace("</p>", "")
                )
        if "United States" in country:
            country = "US"
        if "China" in country:
            country = "CN"
        if "United Kingdom" in country:
            country = "GB"
        if "Japan" in country:
            country = "JP"
        if "South Korea" in country:
            country = "KR"
        if "Netherlands" in country:
            country = "NL"
        if "Germany" in country:
            country = "DE"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
