import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("baskinrobbins_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    coords = ["35,-110", "45,-95", "35,-85", "45,-75", "21,-155", "60,-150"]
    for coord in coords:
        latc = coord.split(",")[0]
        lngc = coord.split(",")[1]
        url = (
            "https://api.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?radius=1500&attributes=&disposition=IN_STORE&latitude="
            + latc
            + "&longitude="
            + lngc
            + "&maxResults=1000&tenant=br-us"
        )
        logger.info(url)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        items = array["getStoresResult"]["stores"]
        for item in items:
            name = "Baskin Robbins"
            typ = "Store"
            store = item["storeId"]
            city = item["city"]
            add = item["street"]
            state = item["state"]
            country = "US"
            zc = item["zipCode"]
            lat = item["latitude"]
            lng = item["longitude"]
            loc = "https://order.baskinrobbins.com/store-selection"
            website = "baskinrobbins.com"
            status = item["status"]
            if "INACTIVE" in status:
                name = name + " - Temporarily Closed"
            try:
                phone = item["phoneNumber"]
            except:
                phone = "<MISSING>"
            try:
                hours = (
                    "Mon: "
                    + item["storeHours"][0]["monday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["monday"]["closeTime"]["timeString"].split(
                        ","
                    )[0]
                )
                hours = (
                    hours
                    + "; Tue: "
                    + item["storeHours"][0]["tuesday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["tuesday"]["closeTime"]["timeString"].split(
                        ","
                    )[0]
                )
                hours = (
                    hours
                    + "; Wed: "
                    + item["storeHours"][0]["wednesday"]["openTime"][
                        "timeString"
                    ].split(",")[0]
                    + "-"
                    + item["storeHours"][0]["wednesday"]["closeTime"][
                        "timeString"
                    ].split(",")[0]
                )
                hours = (
                    hours
                    + "; Thu: "
                    + item["storeHours"][0]["thursday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["thursday"]["closeTime"][
                        "timeString"
                    ].split(",")[0]
                )
                hours = (
                    hours
                    + "; Fri: "
                    + item["storeHours"][0]["friday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["friday"]["closeTime"]["timeString"].split(
                        ","
                    )[0]
                )
                hours = (
                    hours
                    + "; Sat: "
                    + item["storeHours"][0]["saturday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["saturday"]["closeTime"][
                        "timeString"
                    ].split(",")[0]
                )
                hours = (
                    hours
                    + "; Sun: "
                    + item["storeHours"][0]["sunday"]["openTime"]["timeString"].split(
                        ","
                    )[0]
                    + "-"
                    + item["storeHours"][0]["sunday"]["closeTime"]["timeString"].split(
                        ","
                    )[0]
                )
            except:
                hours = "<MISSING>"
            if add != "":
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
