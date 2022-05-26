from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("doyourumble_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://members.rumbleboxinggym.com/api/brands/rumble/locations?geoip=67.220.10.166&open_status=external&limit=100&offer_slug="
    r = session.get(url, headers=headers)
    website = "doyourumble.com"
    typ = "<MISSING>"
    for item in json.loads(r.content)["locations"]:
        try:
            loc = item["site_url"]
        except:
            loc = "<MISSING>"
        store = item["clubready_id"]
        name = item["name"]
        lat = item["lat"]
        lng = item["lng"]
        add = item["address"]
        try:
            add = add + " " + item["address2"]
        except:
            pass
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        country = item["country_code"]
        try:
            phone = item["phone"]
        except:
            phone = "<MISSING>"
        hours = "<MISSING>"
        cs = item["coming_soon"]
        if "Upper East Side" in name:
            loc = "https://www.rumbleboxinggym.com/location-training/upper-east-side-training"
        if "Palo Alto" in name:
            loc = "https://www.rumbleboxinggym.com/location-signature/palo-alto"
        if cs is False:
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
