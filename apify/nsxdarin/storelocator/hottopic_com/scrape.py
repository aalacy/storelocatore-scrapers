from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.hottopic.com/on/demandware.store/Sites-hottopic-Site/default/Stores-FindStores?showMap=false&radius=5000&stateCode=&lat=34.0522342&long=-118.2436849"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"ID": "' in line:
            store = line.split('"ID": "')[1].split('"')[0]
            hours = ""
        if '"name": "' in line:
            name = line.split('"name": "')[1].split('"')[0]
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"address2": "' in line:
            add = add + " " + line.split('"address2": "')[1].split('"')[0]
            add = add.strip()
        if '"postalCode": "' in line:
            zc = line.split('"postalCode": "')[1].split('"')[0]
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"stateCode": "' in line:
            state = line.split('"stateCode": "')[1].split('"')[0]
        if '"countryCode": "' in line:
            country = line.split('"countryCode": "')[1].split('"')[0]
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"latitude": ' in line:
            lat = line.split('"latitude": ')[1].split(",")[0]
        if '"longitude": ' in line:
            lng = line.split('"longitude": ')[1].split(",")[0]
        if '"storeHours": "' in line:
            days = line.split("<span class='store-hours-day'>")
            for day in days:
                if "<span class='store-hours-time'>" in day:
                    hrs = (
                        day.split("<")[0]
                        + ": "
                        + day.split("<span class='store-hours-time'>")[1].split("<")[0]
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
        if '"distance": "' in line:
            if phone == "":
                phone = "<MISSING>"
            if " " in zc:
                country = "CA"
            website = "hottopic.com"
            typ = "Store"
            loc = "https://www.hottopic.com/store-details?StoreId=" + store
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
