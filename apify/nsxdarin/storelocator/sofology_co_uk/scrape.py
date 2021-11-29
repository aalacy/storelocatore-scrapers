from sgrequests import SgRequests
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://api.sofology.co.uk/api/store/"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        website = "sofology.co.uk"
        name = item["outlet"]
        store = item["id"]
        try:
            add = item["addressOne"] + " " + item["addressTwo"]
        except:
            add = item["addressOne"]
        zc = item["postCode"]
        state = "<MISSING>"
        city = item["town"]
        country = "GB"
        phone = item["phone"]
        hours = (
            item["openingTimes"]
            .replace("</li><li>", "; ")
            .replace("<li>", "")
            .replace("<span>", "")
            .replace("</li>", "")
            .replace("</span>", "")
            .replace("  ", " ")
        )
        purl = "https://www.sofology.co.uk/stores/" + name.lower().replace(" ", "-")
        lat = item["lat"]
        lng = item["lng"]
        typ = "<MISSING>"
        if name == "Croydon":
            city = "Croydon"
        if name == "Blackburn":
            hours = "Mon - Fri: 10am - 8pm; Saturday:10am - 6pm; Sunday: 11am - 5pm"
        if phone != "":
            yield SgRecord(
                locator_domain=website,
                page_url=purl,
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
