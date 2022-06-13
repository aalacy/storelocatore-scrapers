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

    url = "https://beddingplusmattress.com/locations/"
    r = session.get(url, headers=headers)
    loclist = r.text.split('{"locations":', 1)[1].split(',"displayLocations"', 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["title"]
        phone = loc["phone"]["text"]
        lat = loc["lat"]
        longt = loc["long"]
        address = loc["address"]
        street, state = address.split(", ", 1)
        city = street.split(" ")[-1]
        street = street.replace(city, "")
        state, pcode = state.split(" ", 1)
        yield SgRecord(
            locator_domain="https://beddingplusmattress.com/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
