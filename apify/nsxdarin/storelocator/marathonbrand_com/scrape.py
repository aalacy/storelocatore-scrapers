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
    url = "https://marathon.shotgunflat.com/data.txt"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        items = line.split("Marathon Gas - ")
        for item in items:
            if "|" in item:
                name = item.split("|")[0]
                add = item.split("|")[1]
                lat = item.split("|")[2]
                lng = item.split("|")[3]
                store = "<MISSING>"
                hours = "<MISSING>"
                website = "marathonabrand.com"
                typ = "<MISSING>"
                city = item.split("|")[5]
                state = item.split("|")[6]
                country = "US"
                phone = item.split("|")[8]
                zc = item.split("|")[7]
                loc = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
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
