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
    url = (
        "https://www.marathonbrand.com/content/includes/mpc-brand-stations/SiteList.csv"
    )
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "StoreName" not in line:
            name = line.split(",")[0]
            add = line.split(",")[2]
            city = line.split(",")[3]
            state = line.split(",")[4]
            store = line.split(",")[1]
            hours = "<MISSING>"
            website = "marathonabrand.com"
            typ = "<MISSING>"
            lat = line.split(",")[7]
            lng = line.split(",")[8]
            country = "US"
            phone = line.split(",")[6]
            zc = line.split(",")[5]
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
