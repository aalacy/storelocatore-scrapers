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
    url = "https://cdn.shopify.com/s/files/1/0397/6842/4614/t/8/assets/stores-map.js"
    r = session.get(url, headers=headers)
    website = "mothersnutritionalcenter.com"
    typ = "<MISSING>"
    country = "US"
    for line in r.iter_lines():
        if "<p><strong>" in line:
            items = line.split("<p><strong>")
            for item in items:
                if "api=1&destination" in item:
                    name = item.split("<")[0].replace("\\", "")
                    store = name.rsplit(" ", 1)[1]
                    hours = (
                        item.split("Store Hours: ")[1].split("<")[0].replace(" |", ";")
                    )
                    add = (
                        item.split("</p><p>")[2].split(",")[0].strip().replace('"', "")
                    )
                    city = (
                        item.split("</p><p>")[2].split(",")[1].strip().rsplit(" ", 1)[0]
                    )
                    state = (
                        item.split("</p><p>")[2].split(",")[1].strip().rsplit(" ", 1)[1]
                    )
                    zc = (
                        item.split("?api=1&destination")[1]
                        .split("'")[0]
                        .rsplit("+", 1)[1]
                    )
                    lat = item.split("</a></p>',")[1].split(",")[0].strip()
                    lng = item.split("</a></p>',")[1].split(",")[1].strip()
                    phone = "<MISSING>"
                    loc = "https://mothersnc.com/pages/stores"
                    state = city.rsplit(" ", 1)[1]
                    city = city.rsplit(" ", 1)[0]
                    zc = zc.replace("\\", "").replace("/", "").strip()
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
