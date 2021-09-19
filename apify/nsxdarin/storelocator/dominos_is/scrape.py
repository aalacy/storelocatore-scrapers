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

logger = SgLogSetup().get_logger("dominos_is")


def fetch_data():
    url = "https://www.dominos.is/en/locations"
    r = session.get(url, headers=headers)
    website = "dominos.is"
    typ = "<MISSING>"
    country = "IS"
    loc = "<MISSING>"
    phone = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"shops":[' in line:
            items = line.split('"shops":[')[1].split('"meta":{"Id"')[0].split('"ID":')
            for item in items:
                if '"Address":"' in item:
                    store = item.split(",")[0]
                    add = item.split('"Address":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = "<MISSING>"
                    name = add
                    hours = (
                        item.split('"OpeningHours":"')[1]
                        .split('"')[0]
                        .replace("\\u003cbr\\u003e", "; ")
                    )
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    loc = "<MISSING>"
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    hours = hours.replace("\\n", "").replace(" ;", ";").strip()
                    if "; DELIVERY" in hours:
                        hours = hours.split("; DELIVERY")[0].strip()
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
