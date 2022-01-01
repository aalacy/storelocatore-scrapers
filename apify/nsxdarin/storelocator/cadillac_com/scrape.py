from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("cadillac_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "locale": "en_US",
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    for clat, clng in search:
        url = (
            "https://www.cadillac.com/OCRestServices/dealer/latlong/v1/Cadillac/"
            + str(clat)
            + "/"
            + str(clng)
            + "/?distance=500&maxResults=500"
        )
        logger.info("Pulling Lat-Long %s,%s..." % (str(clat), str(clng)))
        try:
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"id":' in line:
                    items = line.split('"id":')
                    for item in items:
                        if '"dealerName":"' in item:
                            name = item.split('"dealerName":"')[1].split('"')[0]
                            store = item.split(",")[0]
                            lat = item.split('"latitude":')[1].split(",")[0]
                            lng = item.split('"longitude":')[1].split("}")[0]
                            add = item.split('"addressLine1":"')[1].split('"')[0]
                            if "addressLine2" in item:
                                add = (
                                    add
                                    + " "
                                    + item.split('"addressLine2":"')[1].split('"')[0]
                                )
                            city = item.split('"cityName":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            state = item.split('"countrySubdivisionCode":"')[1].split(
                                '"'
                            )[0]
                            country = item.split('"countryIso":"')[1].split('"')[0]
                            phone = item.split('{"phone1":"')[1].split('"')[0]
                            typ = "Dealer"
                            try:
                                purl = item.split('"dealerUrl":"')[1].split('"')[0]
                            except:
                                purl = "<MISSING>"
                            website = "cadillac.com"
                            hours = ""
                            if '"generalOpeningHour":[' in item:
                                hrs = item.split('"generalOpeningHour":[')[1].split(
                                    '}],"serviceOpeningHour"'
                                )[0]
                                days = hrs.split('"openFrom":"')
                                for day in days:
                                    if '"openTo":"' in day:
                                        if hours == "":
                                            hours = (
                                                day.split('"dayOfWeek":[')[1]
                                                .split("]")[0]
                                                .replace("1", "Mon")
                                                .replace("2", "Tue")
                                                .replace("3", "Wed")
                                                .replace("4", "Thu")
                                                .replace("5", "Fri")
                                                .replace("6", "Sat")
                                                .replace("7", "Sun")
                                                + ": "
                                                + day.split('"')[0]
                                                + "-"
                                                + day.split('"openTo":"')[1].split('"')[
                                                    0
                                                ]
                                            )
                                        else:
                                            hours = (
                                                hours
                                                + "; "
                                                + day.split('"dayOfWeek":[')[1]
                                                .split("]")[0]
                                                .replace("1", "Mon")
                                                .replace("2", "Tue")
                                                .replace("3", "Wed")
                                                .replace("4", "Thu")
                                                .replace("5", "Fri")
                                                .replace("6", "Sat")
                                                .replace("7", "Sun")
                                                + ": "
                                                + day.split('"')[0]
                                                + "-"
                                                + day.split('"openTo":"')[1].split('"')[
                                                    0
                                                ]
                                            )
                            else:
                                hours = "<MISSING>"
                            if len(zc) == 9:
                                zc = zc[:5] + "-" + zc[-4:]
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
        except:
            pass


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
