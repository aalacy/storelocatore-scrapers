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

logger = SgLogSetup().get_logger("ballarddesigns_com")


def fetch_data():
    url = "https://www.ballarddesigns.com/wcsstore/images/BallardDesigns/_media/locations/store-location-info.json"
    r = session.get(url, headers=headers)
    website = "ballarddesigns.com"
    typ = "<MISSING>"
    country = "US"
    for line in r.iter_lines():
        if '"storePageURL": "' in line:
            loc = (
                "https://www.ballarddesigns.com/"
                + line.split('"storePageURL": "')[1].split('"')[0]
            )
        if '"storeName": "' in line:
            name = line.split('"storeName": "')[1].split('"')[0]
        if '"storeCode": "' in line:
            store = line.split('"storeCode": "')[1].split('"')[0]
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"address2": "' in line:
            add = add + " " + line.split('"address2": "')[1].split('"')[0]
            add = add.strip()
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"stateAbbr": "' in line:
            state = line.split('"stateAbbr": "')[1].split('"')[0]
        if '"zipCode": "' in line:
            zc = line.split('"zipCode": "')[1].split('"')[0]
        if '"telephone": "' in line:
            phone = line.split('"telephone": "')[1].split('"')[0]
        if '"latitude": ' in line:
            lat = line.split('"latitude": ')[1].split(",")[0]
        if '"longitude":' in line:
            lng = (
                line.split('"longitude":')[1]
                .strip()
                .replace("\r", "")
                .replace("\n", "")
            )
            hours = "<MISSING>"
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
