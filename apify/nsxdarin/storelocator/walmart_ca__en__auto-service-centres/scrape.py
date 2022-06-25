from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import tenacity
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("walmart_ca__en__auto-service-centres")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = static_zipcode_list(1, SearchableCountries.CANADA)


@tenacity.retry(stop=tenacity.stop_after_attempt(7), wait=tenacity.wait_fixed(7))
def fetch_stores(http, code):
    logger.info(f"Pulling Zip Code: {code}...")
    formatted_code = code.replace(" ", "")
    url = f"https://www.walmart.ca/en/stores-near-me/api/searchStores?singleLineAddr={formatted_code}&serviceTypes=TIRE_AND_LUBE_EXPRESS_CENTRE"
    return http.get(url, headers=headers).json()["payload"]["stores"]


def fetch_data():
    with SgRequests(
        proxy_escalation_order=[
            "http://groups-RESIDENTIAL,country-{}:{}@proxy.apify.com:8000/"
        ]
    ) as http:
        website = "walmart.ca/en/auto-service-centres"
        typ = "Walmart"
        country = "CA"
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_stores, http, code) for code in search]
        for future in as_completed(futures):
            stores = future.result()
            for item in stores:
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
                hours = ""
                for svc in item["servicesMap"]:
                    svcname = svc["service"]["name"]
                    if "TIRE_AND_LUBE_EXPRESS_CENTRE" in svcname:
                        Fuel = True
                        for day in svc["regularHours"]:
                            try:
                                hrs = day["day"] + ": " + day["start"] + "-" + day["end"]
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


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
