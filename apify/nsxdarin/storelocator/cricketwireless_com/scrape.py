from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("cricketwireless_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    for search_lat, search_lng in search:
        logger.info("Pulling %s-%s..." % (str(search_lat), str(search_lng)))
        url = (
            "https://api.momentfeed.com/v1/analytics/api/llp/cricket.json?auth_token=IVNLPNUOBXFPALWE&center="
            + str(search_lat)
            + ","
            + str(search_lng)
            + "&coordinates=40,-90,60,-110&multi_account=false&name=Cricket+Wireless+Authorized+Retailer,Cricket+Wireless+Store&page=1&pageSize=500&type=store"
        )
        r = session.get(url, headers=headers)
        name = ""
        website = "cricketwireless.com"
        country = "US"
        for line in r.iter_lines():
            if '"momentfeed_venue_id":"' in line:
                items = line.split('"momentfeed_venue_id":"')
                for item in items:
                    if '"store_info":' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        typ = item.split('"brand_name":"')[1].split('"')[0]
                        store = item.split('"corporate_id":"')[1].split('"')[0]
                        add = item.split('"address":"')[1].split('"')[0]
                        try:
                            add = (
                                add
                                + " "
                                + item.split('"address_extended":"')[1].split('"')[0]
                            )
                            add = add.strip()
                        except:
                            pass
                        city = item.split('"locality":"')[1].split('"')[0]
                        state = item.split('"region":"')[1].split('"')[0]
                        zc = item.split('"postcode":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        purl = item.split('"website":"')[1].split('"')[0]
                        hours = item.split('"store_hours":"')[1].split('"')[0]
                        hours = hours.replace("1,", "Mon: ").replace(";2,", "; Tue: ")
                        hours = hours.replace(";2,", "; Tue: ")
                        hours = hours.replace(";3,", "; Wed: ")
                        hours = hours.replace(";4,", "; Thu: ")
                        hours = hours.replace(";5,", "; Fri: ")
                        hours = hours.replace(";6,", "; Sat: ")
                        hours = hours.replace(";7,", "; Sun: ")
                        hours = hours.replace(",", "-")
                        hours = hours.replace("1000", "10:00")
                        hours = hours.replace("1100", "11:00")
                        hours = hours.replace("1200", "12:00")
                        hours = hours.replace("1300", "1:00")
                        hours = hours.replace("1400", "2:00")
                        hours = hours.replace("1500", "3:00")
                        hours = hours.replace("1600", "4:00")
                        hours = hours.replace("1700", "5:00")
                        hours = hours.replace("1800", "6:00")
                        hours = hours.replace("1900", "7:00")
                        hours = hours.replace("2000", "8:00")
                        hours = hours.replace("2100", "9:00")
                        hours = hours.replace("2200", "10:00")
                        hours = hours.replace("700", "7:00")
                        hours = hours.replace("800", "8:00")
                        hours = hours.replace("900", "9:00")
                        if hours == "":
                            hours = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if "Sun" not in hours:
                            hours = hours + " Sun: Closed"
                            hours = hours.replace("  ", " ")
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
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
