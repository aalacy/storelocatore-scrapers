from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("lubefast_com")


def fetch_data():
    url = "https://lubefast.com/wp-admin/admin-ajax.php?action=store_search&lat=30.69537&lng=-88.03989&max_results=25&search_radius=50&autoload=1"
    website = "lubefast.com"
    typ = "<MISSING>"
    country = "US"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        add = item["address"]
        hours = ""
        name = item["store"].replace("&#8211;", "-")
        store = item["id"]
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        lat = item["lat"]
        lng = item["lng"]
        phone = item["phone"]
        days = str(item["hours"]).split("<tr><td>")
        for day in days:
            if "</td><td>" in day:
                hrs = (
                    day.split("<")[0]
                    + ": "
                    + day.split("</td><td>")[1].replace("<time>", "").split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        loc = item["url"].replace("\\", "")
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
