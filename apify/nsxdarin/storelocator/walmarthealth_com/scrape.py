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
    max_search_distance_miles=50,
    max_search_results=25,
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
                if '"phone":"' in line:
                    items = line.split('"phone":"')
                    for item in items:
                        if '"clinicServices":' not in item:
                            store = "<MISSING>"
                            name = "Walmart Health"
                            phone = item.split('"')[0]
                            state = item.split('"address":{"state":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            add = item.split('"address1":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            lat = item.split('"latitude":')[1].split(",")[0]
                            lng = item.split('"longitude":')[1].split("}")[0]
                            loc = "<MISSING>"
                            hours = (
                                "Mon-Fri: "
                                + item.split('"monToFriHrs":{"startHr":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"monToFriHrs":{"')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sat: "
                                + item.split('"saturdayHrs":{"startHr":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"saturdayHrs":{"')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sun: "
                                + item.split('"sundayHrs":{"startHr":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"sundayHrs":{"')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
