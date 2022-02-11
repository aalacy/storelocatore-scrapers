from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()

logger = SgLogSetup().get_logger("bananamoondaynursery_co_uk")


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    url = "https://www.bananamoondaynursery.co.uk"
    r = session.get(url, headers=headers)
    csrf = ""
    for line in r.iter_lines():
        if 'name="csrf-token" content="' in line:
            csrf = line.split('name="csrf-token" content="')[1].split('"')[0]
    url = "https://www.bananamoondaynursery.co.uk/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "content-type": "application/json;charset=UTF-8",
        "referer": "https://www.bananamoondaynursery.co.uk/",
        "origin": "https://www.bananamoondaynursery.co.uk",
        "x-csrf-token": csrf,
        "x-requested-with": "XMLHttpRequest",
    }
    payload = {
        "postcode": {
            "text": "",
            "icon": {"url": "/img/marker--secondary.png"},
            "position": {},
        }
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "bananamoondaynursery.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["locations"]:
        name = item["name"]
        loc = "https://www.bananamoondaynursery.co.uk/find-us/" + item["slug"]
        lat = item["position"]["lat"]
        lng = item["position"]["lng"]
        add = item["address"]["line_1"]
        try:
            add = add + " " + item["address"]["line_2"]
        except:
            pass
        city = item["address"]["city"]
        state = "<MISSING>"
        zc = item["address"]["postcode"]
        phone = item["telephone"]
        hours = "Sun-Sat: " + item["start_time"] + "-" + item["end_time"]
        store = "<MISSING>"
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
