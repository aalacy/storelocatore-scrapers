from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from tenacity import retry, stop_after_attempt
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ford_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance=None,
    max_search_results=None,
)


@retry(stop=stop_after_attempt(10))
def fetch_zip_code(url):
    session = SgRequests()
    return session.get(url, headers=headers, timeout=10).json()


def fetch_data():
    for code in search:
        url = (
            "https://www.ford.com/services/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&postalCode="
            + code
            + "&api_key=0d571406-82e4-2b65-cc885011-048eb263"
        )
        js = fetch_zip_code(url)
        if "Dealer" in js["Response"]:
            dealers = (
                js["Response"]["Dealer"]
                if isinstance(js["Response"]["Dealer"], list)
                else [js["Response"]["Dealer"]]
            )
            for item in dealers:
                lng = item["Longitude"]
                lat = item["Latitude"]
                name = item["Name"]
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
                if hours == "":
                    hours = "<MISSING>"
                if purl == "":
                    purl = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
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
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
