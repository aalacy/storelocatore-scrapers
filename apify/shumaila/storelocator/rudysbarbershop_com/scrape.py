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

    url = "https://rudysbarbershop.com/pages/locations"
    r = session.get(url, headers=headers)
    loclist = r.text.split("shopData.push(")[1:]
    for loc in loclist:
        loc = (
            loc.split(");", 1)[0].replace("parseFloat(", "").replace('")', '"').strip()
        )
        loc = json.loads(loc)
        store = loc["id"]
        title = loc["title"]
        address = loc["address"]
        city = loc["city"]
        state = loc["state"]

        street, pcode = address.split(city + " " + state + ", ", 1)
        phone = loc["phone"]
        hours = loc["hours"].replace("<br />", " ").strip()
        lat = loc["latitude"]
        longt = loc["longitude"]

        link = "https://rudysbarbershop.com" + loc["url"]

        yield SgRecord(
            locator_domain="https://rudysbarbershop.com/",
            page_url=link,
            location_name=title,
            street_address=street.replace("<br>", " ").strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.replace(",", "").strip(),
            country_code="US",
            store_number=str(store),
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
