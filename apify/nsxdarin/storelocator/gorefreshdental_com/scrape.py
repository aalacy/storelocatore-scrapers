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

logger = SgLogSetup().get_logger("gorefreshdental_com")


def fetch_data():
    url = "https://www.gorefreshdental.com/wp-admin/admin-ajax.php?action=store_search&lat=40.440625&lng=-79.995886&max_results=25&search_radius=200&autoload=1"
    r = session.get(url, headers=headers)
    website = "gorefreshdental.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        add = item["address"]
        name = item["store"]
        store = item["id"]
        loc = item["permalink"].replace("\\", "")
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        lat = item["lat"]
        lng = item["lng"]
        phone = item["phone"]
        try:
            hours = item["hours"]
        except:
            hours = ""
        if hours is None:
            hours = "<MISSING>"
        hours = (
            hours.replace("</td><td><time>", ": ")
            .replace("</time></td></tr><tr><td>", "; ")
            .replace(
                '<table role=\\"presentation\\" class=\\"wpsl-opening-hours\\"><tr><td>',
                "",
            )
        )
        hours = hours.replace("</td></tr></table>", "")
        hours = hours.replace("</td></tr><tr><td>", "; ").replace("</td><td>", ": ")
        if "<td>" in hours:
            hours = hours.rsplit("<td>", 1)[1]
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
