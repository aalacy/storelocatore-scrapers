from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ford_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "application-id": "07152898-698b-456e-be56-d3d83011d0a6",
}


def fetch_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )

    for code in search:
        logger.info(code)
        url = (
            "https://www.ford.com/cxservices/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&postalCode="
            + code
        )

        try:
            with SgRequests() as session:
                logger.info(f"PullingContentFrom: {url} | (zip, {code})")
                r = session.get(url, headers=headers)
                logger.info(f"(HTTPStatusCode: {r.status_code}, ZIP: {code})")
                if r.status_code != 200:
                    search.found_nothing()
                    continue
                js = r.json()
                if not js:
                    search.found_nothing()
                if "Dealer" in js["Response"]:
                    dealers = (
                        js["Response"]["Dealer"]
                        if isinstance(js["Response"]["Dealer"], list)
                        else [js["Response"]["Dealer"]]
                    )
                    logger.info(f"({len(dealers)} Stores Found, {code})")
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
                        if lng and lat:
                            search.found_location_at(lat, lng)
                        else:
                            search.found_nothing()

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
                else:
                    search.found_nothing()
                    continue
        except Exception as e:
            logger.info(f"FixFetchRecordError: << {e} >> (ZIP, {code})")


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
