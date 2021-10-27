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
    url = "https://api.freshop.com/1/stores?app_key=foodland_unfi&has_address=true&limit=-1&token=4c137e263f44eb7fc616859a23238e13"
    r = session.get(url, headers=headers)
    website = "foodlandstores.com"
    country = "US"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"name":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    loc = item.split('"url":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_0":"')[1].split('"')[0]
                    except:
                        add = ""
                    add = add + " " + item.split('"address_1":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    hours = item.split('"hours_md":"')[1].split('"')[0]
                    phone = item.split('"phone_md":"')[1].split('"')[0]
                    hours = hours.replace("Hours: ", "")
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
