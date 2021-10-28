from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    typ = "<MISSING>"
    website = "whbm.com"
    url = "https://www.whitehouseblackmarket.com/locations/modules/multilocation/?near_location=55441&services__in=&language_code=en-us&published=1&within_business=true&limit=500"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)["objects"]:
        zc = item["postal_code"]
        phone = item["phonemap_e164"]["phone"]
        store = item["id"]
        loc = item["location_url"]
        city = item["city"]
        name = item["location_name"]
        lat = item["lat"]
        lng = item["lon"]
        state = item["state"]
        country = item["country"]
        add = item["street"]
        hours = item["hours_by_type"]["primary"]["hours"]
        hrs = "Mon: " + str(hours[0]).replace("[", "").replace("]", "").replace(
            "', '", "-"
        )
        hrs = (
            hrs
            + "; Tue: "
            + str(hours[1]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs
            + "; Wed: "
            + str(hours[2]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs
            + "; Thu: "
            + str(hours[3]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs
            + "; Fri: "
            + str(hours[4]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs
            + "; Sat: "
            + str(hours[5]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs
            + "; Sun: "
            + str(hours[6]).replace("[", "").replace("]", "").replace("', '", "-")
        )
        hrs = (
            hrs.replace(":00;", ";")
            .replace(":00'", "")
            .replace(":00-", "-")
            .replace("'", "")
        )
        hrs = hrs.replace(": ;", ": Closed")
        hours = hrs
        if ":" not in hours.split("Sun:")[1]:
            hours = hours + " Closed"
        if country == "CA" or country == "US":
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
