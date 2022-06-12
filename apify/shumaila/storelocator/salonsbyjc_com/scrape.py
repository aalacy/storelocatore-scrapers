from bs4 import BeautifulSoup
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

    url = "https://salonsbyjc.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.712891&max_results=200&search_radius=25&autoload=1"
    loclist = session.get(url, headers=headers).json()
    for loc in loclist:
        street = loc["address"] + str(loc["address2"])
        title = loc["store"]
        store = loc["id"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        ccode = "US"
        if "USA" not in loc["country"]:
            ccode = "CA"
        link = "https://salonsbyjc.com" + loc["url"]
        hours = (
            BeautifulSoup(loc["hours"], "html.parser")
            .text.replace("PM", "PM ")
            .replace("day", "day ")
            .replace("losed", "losed ")
        )

        yield SgRecord(
            locator_domain="https://salonsbyjc.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=store,
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
