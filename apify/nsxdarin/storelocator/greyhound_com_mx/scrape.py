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

logger = SgLogSetup().get_logger("greyhound_com_mx")


def fetch_data():
    url = "https://bustracker.greyhound.com/stop-finder/"
    r = session.get(url, headers=headers)
    website = "greyhound.com.mx"
    typ = "<MISSING>"
    country = "MX"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '"id" : "' in line:
            Mexico = False
            store = line.split('"id" : "')[1].split('"')[0]
            loc = "https://bustracker.greyhound.com/stops/" + store
        if '"name" : "' in line:
            name = line.split('"name" : "')[1].split('"')[0]
        if '"shortName" : "' in line and ', MX",' in line:
            Mexico = True
            add = name.split(":")[1].split(",")[0].strip()
            name = name.split(":")[0].strip()
        if '"place" : "' in line:
            city = line.split('"place" : "')[1].split('"')[0]
            state = "<MISSING>"
            hours = "<MISSING>"
            phone = "<MISSING>"
            zc = "<MISSING>"
        if '"stopLatitude" : ' in line:
            lat = line.split('"stopLatitude" : ')[1].split(",")[0]
        if '"stopLongitude" : ' in line:
            lng = line.split('"stopLongitude" : ')[1].split(",")[0]
            if Mexico:
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
