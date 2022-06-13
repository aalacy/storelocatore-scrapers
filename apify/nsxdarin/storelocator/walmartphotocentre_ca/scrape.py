from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("walmartphotocentre_ca")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    for code in search:
        Retry = True
        rc = 0
        while Retry and rc <= 5:
            Retry = False
            rc = rc + 1
            try:
                logger.info(("Pulling Zip Code %s..." % code))
                url = (
                    "https://www.walmart.ca/en/stores-near-me/api/searchStores?singleLineAddr="
                    + code.replace(" ", "")
                )
                website = "walmartphotocentre.ca"
                typ = "Walmart"
                country = "CA"
                session = SgRequests()
                r2 = session.get(url, headers=headers)
                for item in json.loads(r2.content)["payload"]["stores"]:
                    Fuel = False
                    try:
                        name = item["displayName"]
                    except:
                        name = item["address"]["city"]
                    store = item["id"]
                    add = item["address"]["address1"]
                    try:
                        add = add + " " + item["address"]["address2"]
                    except:
                        pass
                    city = item["address"]["city"]
                    state = item["address"]["state"]
                    zc = item["address"]["postalCode"]
                    phone = item["phone"]
                    lat = item["geoPoint"]["latitude"]
                    lng = item["geoPoint"]["longitude"]
                    found_location_at(lat, lng)
                    hours = ""
                    for svc in item["servicesMap"]:
                        svcname = svc["service"]["name"]
                        if "WALMART_PHOTO_CENTRE" in svcname:
                            Fuel = True
                            for day in svc["regularHours"]:
                                try:
                                    hrs = (
                                        day["day"]
                                        + ": "
                                        + day["start"]
                                        + "-"
                                        + day["end"]
                                    )
                                except:
                                    hrs = day["day"] + ": Closed"
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    loc = (
                        "https://www.walmart.ca/en/stores-near-me/"
                        + name.replace(" ", "-").lower()
                        + "-"
                        + str(store)
                    )
                    if "0" not in hours:
                        hours = "<MISSING>"
                    if "Supercentre" in name:
                        typ = "Supercenter"
                    if "Neighborhood Market" in name:
                        typ = "Neighborhood Market"
                    if hours == "":
                        hours = "<MISSING>"
                    if add != "" and Fuel:
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
            except:
                Retry = True
                found_nothing()


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
