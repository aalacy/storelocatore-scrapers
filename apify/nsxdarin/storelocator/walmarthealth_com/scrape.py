from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("walmarthealth_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=10,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    country = "US"
    for zipcode in search:
        typ = "<MISSING>"
        country = "US"
        url = "https://www.walmarthealth.com/api/clinicLocations?zip=" + zipcode
        logger.info(("Pulling Postal Code %s..." % zipcode))
        session = SgRequests()
        try:
            r = session.get(url, headers=headers)
            website = "walmarthealth.com"
            for line in r.iter_lines():
                if '"clinics":' in line:
                    items = line.split('"clinics":')[1].split('"phone":"')
                    for item in items:
                        if ',"operationalHours"' in item:
                            name = "Walmart Health"
                            loc = "https://www.walmarthealth.com/"
                            hrs = (
                                "Mon-Fri: "
                                + item.split('monToFriHrs":{"startHr":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('monToFriHrs":{"startHr":"')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                            try:
                                hrs = (
                                    hrs
                                    + "; Sat: "
                                    + item.split('"saturdayHrs":{')[1]
                                    .split('"startHr":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split('"saturdayHrs":{')[1]
                                    .split('"endHr":"')[1]
                                    .split('"')[0]
                                )
                            except:
                                hrs = hrs + "; Sat: Closed"
                            try:
                                hrs = (
                                    hrs
                                    + "; Sun: "
                                    + item.split('"sundayHrs":{')[1]
                                    .split('"startHr":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split('"sundayHrs":{')[1]
                                    .split('"endHr":"')[1]
                                    .split('"')[0]
                                )
                            except:
                                hrs = hrs + "; Sun: Closed"
                            hours = hrs
                            state = (
                                item.split('"address":')[1]
                                .split('"state":"')[1]
                                .split('"')[0]
                            )
                            city = (
                                item.split('"address":')[1]
                                .split('"city":"')[1]
                                .split('"')[0]
                            )
                            add = item.split('"address1":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            lat = item.split('"latitude":')[1].split(",")[0]
                            lng = item.split('"longitude":')[1].split("}")[0]
                            store = item.split('"storeNbr":"')[1].split('"')[0]
                            phone = item.split('"')[0]
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
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
