from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("oakstreethealth_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.oakstreethealth.com/locations/all"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "oakstreethealth.com"

    states = base.find(class_="footer-nav-item__subnav-inner").find_all("a")

    base_link = "https://ghizbmgvi8-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.12.0)%3B%20Browser%3B%20JS%20Helper%20(3.7.0)"

    headers1 = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.oakstreethealth.com",
        "x-algolia-api-key": "01a7d1dd2b733447055975f3c10e5c52",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-algolia-application-id": "GHIZBMGVI8",
    }

    for i in states:
        search_text = i.text.lower()
        logger.info(search_text)
        js = {
            "requests": [
                {
                    "indexName": "prod_Locations",
                    "params": "hitsPerPage=100&getRankingInfo=true&facets=%5B%22insuranceAccepted%22%2C%22city%22%2C%22insuranceAccepted%22%2C%22region%22%2C%22services%22%5D&tagFilters=&facetFilters=%5B%5B%22region%3A"
                    + search_text
                    + "%22%5D%5D",
                },
                {
                    "indexName": "prod_Locations",
                    "params": "hitsPerPage=1&getRankingInfo=true&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=region",
                },
            ]
        }
        stores = session.post(base_link, headers=headers1, json=js).json()["results"][
            0
        ]["hits"]

        for store_data in stores:
            link = store_data["url"]
            location_name = store_data["locationName"]
            try:
                street_address = (
                    store_data["streetAddress1"] + " " + store_data["streetAddress2"]
                )
            except:
                street_address = store_data["streetAddress1"]
            city = store_data["city"]
            state = store_data["state"]
            zip_code = store_data["zipCode"]
            country_code = "US"
            location_type = ", ".join(store_data["services"])
            store_number = ""
            latitude = store_data["_geoloc"]["lat"]
            longitude = store_data["_geoloc"]["lng"]

            logger.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            phone = base.find(class_="flex-1 tabular-nums").text.strip()
            try:
                hours_of_operation = " ".join(
                    list(base.find_all(class_="flex items-start")[-1].stripped_strings)
                )
                if "day" not in hours_of_operation.lower():
                    hours_of_operation = "<MISSING>"
            except:
                hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
