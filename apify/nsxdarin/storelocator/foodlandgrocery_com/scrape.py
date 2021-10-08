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
    urls = [
        "https://www.foodlandgrocery.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=0533f43398&load_all=1&layout=1"
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "foodlandgrocery.com"
        typ = "<MISSING>"
        country = "US"
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if ',"street":"' in item:
                        name = item.split('"title":"')[1].split('"')[0]
                        lat = item.split('"lat":"')[1].split('"')[0]
                        lng = item.split('"lng":"')[1].split('"')[0]
                        add = item.split('"street":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        store = item.split('"')[0]
                        loc = "https://www.foodlandgrocery.com/" + item.split(
                            '"website":"'
                        )[1].split('"')[0].replace("\\", "")
                        loc = loc.replace("/http:///", "/")
                        loc = loc.replace(".com//", ".com/")
                        hours = item.split('"open_hours":"{\\"')[1].split('"]}","')[0]
                        hours = (
                            hours.replace('\\":[\\"', ": ")
                            .replace('\\"],\\"', "; ")
                            .replace("\\", "")
                        )
                        name = name.replace("\\u2019", "'")
                        if "boaz-foodland" in loc:
                            phone = "(256) 593-7206"
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
