import json
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
    url = "https://www.booker.co.uk/help/branch-locator"
    r = session.get(url, headers=headers)
    loclist = r.text.split("geoLocations=", 1)[1].split(";", 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        city = title = loc[0]
        lat = loc[1]
        longt = loc[2]
        street = loc[3]
        pcode = loc[4]
        phone = loc[5]
        store = loc[6]
        if lat == 0:
            lat = longt = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.booker.co.uk/",
            page_url=SgRecord.MISSING,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.replace(",", "").strip(),
            country_code="GB",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
