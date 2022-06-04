from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_locations(retry=0):
    try:
        session = SgRequests()
        url = "https://www.marathonbrand.com/content/includes/mpc-brand-stations/SiteList.csv"
        wayback_data = session.get(
            f"http://archive.org/wayback/available?url={url}"
        ).json()
        data_url = wayback_data["archived_snapshots"]["closest"]["url"]

        return session.get(data_url, headers=headers).iter_lines()
    except:
        if retry < 10:
            return get_locations(retry + 1)


def fetch_data():
    for line in get_locations():
        if "StoreName" not in line:
            name = line.split(",")[0]
            add = line.split(",")[2]
            city = line.split(",")[3]
            state = line.split(",")[4]
            store = line.split(",")[1]
            hours = "<MISSING>"
            website = "marathonabrand.com"
            typ = "<MISSING>"
            lat = line.split(",")[8]
            lng = line.split(",")[7]
            country = "US"
            phone = line.split(",")[6]
            zc = line.split(",")[5]
            zc = f"{zc[:5]}-{zc[5:]}"
            loc = "https://www.marathonbrand.com/Stations/Station_Locator/"
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
