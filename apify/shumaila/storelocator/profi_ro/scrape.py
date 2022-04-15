import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.profi.ro/magazine/"
    r = session.get(url, headers=headers)
    loclist = (
        r.text.split("const STORE_LOCATIONS = ", 1)[1]
        .split("const CURRENT_DATE", 1)[0]
        .replace(";", " ")
        .strip()
    )

    loclist = json.loads(loclist)
    for loc in loclist:

        store = loc["code"]
        title = loc["title"]
        city = loc["city"]
        link = "https://www.profi.ro/magazine/#" + loc["url"]
        street = loc["address"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        phone = loc["phone"]
        hours = loc["open_mf_s"]

        yield SgRecord(
            locator_domain="https://www.profi.ro/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="RO",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
