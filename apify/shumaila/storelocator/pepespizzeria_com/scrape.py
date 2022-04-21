from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://admin.pepespizzeria.com/api/v1/restaurants"
    divlist = session.get(url, headers=headers).json()["data"]["restaurants"]
    for div in divlist:
        loclist = divlist[div]
        for loc in loclist:
            store = loc["id"]
            link = "https://order.pepespizzeria.com/store/" + loc["slug"]
            title = loc["name"]
            phone = loc["telephone"]
            street = loc["street_address"]
            city = loc["city"]
            pcode = loc["zip"]
            state = loc["state"]
            ccode = loc["country"]
            lat, longt = loc["directions"].split("=", 1)[1].split(",", 1)
            yield SgRecord(
                locator_domain="https://order.pepespizzeria.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=SgRecord.MISSING,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
