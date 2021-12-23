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

logger = SgLogSetup().get_logger("landrysseafood_com")


def fetch_data():
    url = "https://www.landrysseafood.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "landrysseafood.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"id": ' in line:
            items = line.split('{"id": ')
            for item in items:
                if '"url": "' in item:
                    loc = (
                        "https://www.landrysseafood.com"
                        + item.split('"url": "')[1].split('"')[0]
                    )
                    name = item.split('"name": "')[1].split('"')[0]
                    hours = item.split('"hours": "\\u003cp\\u003e')[1].split("u003ch4")[
                        0
                    ]
                    hours = hours.replace("\\u003cbr/\\u003e", "; ")
                    add = item.split('"street": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    zc = item.split('"postal_code": "')[1].split('"')[0]
                    lat = item.split('"lat": "')[1].split('"')[0]
                    lng = item.split('"lng": "')[1].split('"')[0]
                    phone = item.split('"phone_number": "')[1].split('"')[0]
                    store = "<MISSING>"
                    hours = hours.replace("\\u0026amp;", "&")
                    hours = hours.replace("\\u0026nbsp;", "")
                    hours = hours.replace("; \\", "")
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
