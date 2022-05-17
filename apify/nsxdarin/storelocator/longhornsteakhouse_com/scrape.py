from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
}

logger = SgLogSetup().get_logger("longhornsteakhouse_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=10,
)


def fetch_data():
    for lat, lng in search:
        llstr = str(lat) + "," + str(lng)
        logger.info(str(lat) + "-" + str(lng))
        url = "https://www.longhornsteakhouse.com/web-api/restaurants"
        payload = {
            "geoCode": llstr,
            "resultsPerPage": 250,
            "resultsOffset": 0,
            "pdEnabled": "",
            "reservationEnabled": "",
            "isToGo": "",
            "privateDiningEnabled": "",
            "isNew": "",
            "displayDistance": True,
            "locale": "en_US",
        }
        r = session.post(url, headers=headers, data=payload)
        try:
            for line in r.iter_lines():
                if '{"country":"' in line:
                    items = line.split('{"country":"')
                    for item in items:
                        if '"enableViewMenu":' in item:
                            try:
                                website = "longhornsteakhouse.com"
                                typ = "<MISSING>"
                                country = "US"
                                add = (
                                    item.split('"AddressOne":"')[1].split('"')[0]
                                    + " "
                                    + item.split('"AddressTwo":"')[1].split('"')[0]
                                )
                                add = add.strip()
                                state = item.split('"state":"')[1].split('"')[0]
                                lat = item.split('"latitude":"')[1].split('"')[0]
                                city = item.split('"city":"')[1].split('"')[0]
                                lng = item.split('"longitude":"')[1].split('"')[0]
                                phone = item.split('"phoneNumber":"')[1].split('"')[0]
                                zc = item.split('"zip":"')[1].split('"')[0][0:5]
                                store = item.split('"displayOrder":')[1].split(",")[0]
                                hours = (
                                    "Sun: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[1]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[1]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Mon: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[2]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[2]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Tue: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[3]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[3]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Wed: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[4]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[4]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Thu: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[5]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[5]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Fri: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[6]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[6]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Sat: "
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[7]
                                    .split('"startTime":"')[1]
                                    .split('"')[0]
                                    + "-"
                                    + item.split(
                                        '"hourTypeDesc":"Hours of Operations"'
                                    )[7]
                                    .split('"endTime":"')[1]
                                    .split('"')[0]
                                )
                                loc = (
                                    "https://www.longhornsteakhouse.com/locations/"
                                    + state.lower()
                                    + "/"
                                    + city.lower()
                                    + "/"
                                    + store
                                )
                                name = item.split('"restaurantName":"')[1].split('"')[0]
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
