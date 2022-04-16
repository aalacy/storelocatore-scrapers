from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ford_ca")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "application-id": "07152898-698b-456e-be56-d3d83011d0a6",
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=50
)


def fetch_data():
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="ca") as session:
        for code in search:
            logger.info(code)
            url = (
                "https://www.ford.ca/cxservices/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&postalCode="
                + code
            )
            try:
                js = session.get(url, headers=headers).json()
                if "Dealer" in js["Response"]:
                    dealers = (
                        js["Response"]["Dealer"]
                        if isinstance(js["Response"]["Dealer"], list)
                        else [js["Response"]["Dealer"]]
                    )
                    for item in dealers:
                        lng = item["Longitude"]
                        lat = item["Latitude"]
                        search.found_location_at(lat, lng)
                        name = item["Name"]
                        logger.info(name)
                        typ = item["dealerType"]
                        website = "ford.com"
                        purl = item["URL"]
                        hours = ""
                        add = (
                            item["Address"]["Street1"]
                            + " "
                            + item["Address"]["Street2"]
                            + " "
                            + item["Address"]["Street3"]
                        )
                        add = add.strip()
                        city = item["Address"]["City"]
                        state = item["Address"]["State"]
                        country = item["Address"]["Country"][:2]
                        zc = item["Address"]["PostalCode"]
                        store = item["SalesCode"]
                        phone = item["Phone"]
                        daytext = str(item["SalesHours"])
                        daytext = daytext.replace("'", '"')
                        daytext = daytext.replace('u"', '"').replace(" {", "{")
                        days = daytext.split(",{")
                        for day in days:
                            if '"name": "' in day:
                                dname = day.split('"name": "')[1].split('"')[0]
                                if '"closed": "true"' in day:
                                    hrs = "Closed"
                                else:
                                    hrs = (
                                        day.split('"open": "')[1].split('"')[0]
                                        + "-"
                                        + day.split('"close": "')[1].split('"')[0]
                                    )
                                if hours == "":
                                    hours = dname + ": " + hrs
                                else:
                                    hours = hours + "; " + dname + ": " + hrs

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
