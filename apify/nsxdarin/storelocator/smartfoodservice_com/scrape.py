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

logger = SgLogSetup().get_logger("smartfoodservice_com")


def fetch_data():
    locs = []
    url = "https://www.smartfoodservice.com/locations/"
    r = session.get(url, headers=headers)
    website = "smartfoodservice.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href = "/locations/store/' in line:
            locs.append(
                "https://www.smartfoodservice.com" + line.split(' = "')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<h1" in line2:
                name = (
                    line2.split("<h1")[1]
                    .split('">')[1]
                    .split("</h2>")[0]
                    .replace("<sup>&reg;</sup>", "")
                )
            if 'name="latitude"' in line2 and lat == "":
                lat = line2.split('value="')[1].split('"')[0]
            if 'name="longitude"' in line2 and lng == "":
                lng = line2.split('value="')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if 'telephone": "' in line2:
                phone = line2.split('telephone": "')[1].split('"')[0]
            if 'name="storeNum"' in line2 and store == "":
                store = line2.split('value="')[1].split('"')[0]
            if '"openingHours": ["' in line2:
                hours = (
                    line2.split('"openingHours": ["')[1]
                    .split('"]')[0]
                    .replace('","', "; ")
                )
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if add != "":
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
