from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("walmart_com/pharmacy")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)


def fetch_data():
    website = "walmart.com/pharmacy"
    for code in search:
        try:
            logger.info(("Pulling Zip Code %s..." % code))
            url = (
                "https://www.walmart.com/store/finder/electrode/api/stores?singleLineAddr="
                + code
                + "&distance=50"
            )
            r2 = session.get(url, headers=headers).json()
            if r2["payload"]["nbrOfStores"]:
                if int(r2["payload"]["nbrOfStores"]) > 0:
                    for store in r2["payload"]["storesData"]["stores"]:
                        if store["geoPoint"] and "PHARM" in str(store):
                            typ = "Walmart Pharmacy"
                            loc = store["detailsPageURL"]
                            snum = store["id"]
                            name = store["displayName"]
                            add = store["address"]["address"]
                            city = store["address"]["city"]
                            state = store["address"]["state"]
                            zc = store["address"]["postalCode"]
                            phone = store["phone"]
                            country = "US"
                            lat = store["geoPoint"]["latitude"]
                            lng = store["geoPoint"]["longitude"]
                            try:
                                hrs = (
                                    "Mon-Fri: "
                                    + str(store)
                                    .split('"name":"PHARMACY"')[1]
                                    .split('"operationalHours":')[1]
                                    .split('"monToFriHrs":')[1]
                                    .split('"startHr":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + str(store)
                                    .split('"name":"PHARMACY"')[1]
                                    .split('"operationalHours":')[1]
                                    .split('"monToFriHrs":')[1]
                                    .split('"endHr":"')[1]
                                    .split('"')[0]
                                )
                                try:
                                    hrs = (
                                        hrs
                                        + "; Sat: "
                                        + str(store)
                                        .split('"name":"PHARMACY"')[1]
                                        .split('"operationalHours":')[1]
                                        .split('"saturdayHrs":')[1]
                                        .split('"startHr":"')[1]
                                        .split('"')[0]
                                        + "-"
                                        + str(store)
                                        .split('"name":"PHARMACY"')[1]
                                        .split('"operationalHours":')[1]
                                        .split('"saturdayHrs":')[1]
                                        .split('"endHr":"')[1]
                                        .split('"')[0]
                                    )
                                except:
                                    hrs = hrs = "; Sat: Closed"
                                try:
                                    hrs = (
                                        hrs
                                        + "; Sun: "
                                        + str(store)
                                        .split('"name":"PHARMACY"')[1]
                                        .split('"operationalHours":')[1]
                                        .split('"sundayHrs":')[1]
                                        .split('"startHr":"')[1]
                                        .split('"')[0]
                                        + "-"
                                        + str(store)
                                        .split('"name":"PHARMACY"')[1]
                                        .split('"operationalHours":')[1]
                                        .split('"sundayHrs":')[1]
                                        .split('"endHr":"')[1]
                                        .split('"')[0]
                                    )
                                except:
                                    hrs = hrs + "; Sun: Closed"
                            except:
                                hrs = "<MISSING>"
                            hours = hrs
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
                                store_number=snum,
                                latitude=lat,
                                longitude=lng,
                                hours_of_operation=hours,
                            )
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()

if __name__ == "__main__":
    scrape()
