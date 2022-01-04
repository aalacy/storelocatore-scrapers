import json
import time
from lxml import html
from concurrent.futures import ThreadPoolExecutor

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

MISSING = "<MISSING>"
website = "wyndhamhotels.com/wyndham"
propertyUrl = "https://www.wyndhamhotels.com/BWSServices/services/search/properties?recordsPerPage=501200&pageNumber=1&brandId=ALL&countryCode="
propertListUrl = "https://www.wyndhamhotels.com/bin/propertyDataList.json"
max_workers = 1

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Connection": "keep-alive",
}

brandMap = {
    "hj": "hojo",
    "HJ": "hojo",
    "hojo": "HJ",
    "lq": "laquinta",
    "LQ": "laquinta",
    "laquinta": "LQ",
    "di": "days-inn",
    "DI": "days-inn",
    "days-inn": "DI",
    "bh": "hawthorn-extended-stay",
    "BH": "hawthorn-extended-stay",
    "hawthorn-extended-stay": "BH",
    "hr": "wyndham",
    "HR": "wyndham",
    "wyndham": "HR",
    "wg": "wingate",
    "WG": "wingate",
    "wingate": "WG",
    "se": "super-8",
    "SE": "super-8",
    "super-8": "SE",
    "bu": "baymont",
    "BU": "baymont",
    "baymont": "BU",
    "dx": "dolce",
    "DX": "dolce",
    "dolce": "DX",
    "dz": "dazzler",
    "DZ": "dazzler",
    "dazzler": "DZ",
    "wr": "wyndham-rewards",
    "WR": "wyndham-rewards",
    "wyndham-rewards": "WR",
    "kg": "knights-inn",
    "KG": "knights-inn",
    "knights-inn": "KG",
    "wt": "tryp",
    "WT": "tryp",
    "tryp": "WT",
    "aa": "americinn",
    "AA": "americinn",
    "americinn": "AA",
    "all": "wyndham-hotel-group",
    "ALL": "wyndham-hotel-group",
    "wyndham-hotel-group": "ALL",
    "ce": "caesars-entertainment",
    "CE": "caesars-entertainment",
    "caesars-entertainment": "CE",
    "mt": "microtel",
    "MT": "microtel",
    "microtel": "MT",
    "gn": "wyndham-garden",
    "GN": "wyndham-garden",
    "wyndham-garden": "GN",
    "gr": "wyndham-grand",
    "GR": "wyndham-grand",
    "wyndham-grand": "GR",
    "es": "esplendor",
    "ES": "esplendor",
    "esplendor": "ES",
    "ra": "ramada",
    "RA": "ramada",
    "ramada": "RA",
    "re": "registry-collection",
    "RE": "registry-collection",
    "registry-collection": "RE",
    "tl": "travelodge",
    "TL": "travelodge",
    "travelodge": "TL",
    "vo": "wyndham-vacations",
    "VO": "wyndham-vacations",
    "wyndham-vacations": "VO",
    "tq": "trademark",
    "TQ": "trademark",
    "trademark": "TQ",
}


def fetchStores():
    response = session.get(propertyUrl, headers=headers)
    data = json.loads(response.text)
    stores = []

    for country in data["countries"]:
        countryName = country["countryName"]
        countryCode = country["countryCode"]

        for state in country["states"]:
            stateName = state["stateName"]
            stateCode = state["stateCode"]

            for city in state["cities"]:
                cityName = city["cityName"]

                for prop in city["propertyList"]:
                    store_number = prop["propertyId"]
                    location_name = prop["propertyName"]
                    brand = prop["brand"]
                    brandId = prop["brandId"]
                    if brandId in brandMap:
                        brand = brandMap[brandId]

                    if prop["tierId"] in brandMap:
                        brand = brandMap[prop["tierId"]]

                    if stateCode == "**":
                        stateName = MISSING
                        page_url_part = countryName
                    else:
                        page_url_part = stateName
                    page_url = f"https://www.wyndhamhotels.com/{brand}/{cityName} {page_url_part}/{prop['uniqueUrl']}/overview".replace(
                        " ", "-"
                    ).lower()
                    stores.append(
                        {
                            "store_number": store_number,
                            "location_name": location_name,
                            "page_url": page_url,
                            "countryCode": countryCode,
                            "state": stateName,
                            "cityName": cityName,
                            "brandId": brandId,
                        }
                    )
    return stores


def getRedirectUrl(store):
    postBody = {
        "locale": "en-us",
        "hotels": [
            {
                "brandId": store["brandId"],
                "hotelId": store["store_number"],
                "hotelCode": store["store_number"],
            }
        ],
    }

    try:
        response = session.post(
            propertListUrl, headers=headers, data=json.dumps(postBody)
        )
        data = json.loads(response.text)
        page_url = data["hotels"][0]["overviewPath"]
        store["ex_page_url"] = store["page_url"]
        store["page_url"] = page_url
        response = session.get(store["page_url"], headers=headers)

        if response.text is None or response.text == "":
            return store, None, None

        if "hotels were found that match your search" in response.text:
            return store, None, None

        body = html.fromstring(response.text, "lxml")
        geoJSON = getScriptWithGeo(body)
        return store, body, geoJSON
    except Exception as e:
        log.info(f"Handling this:\n{e}")
        return store, None, None


def fetchSingleSore(store):
    response = session.get(store["page_url"], headers=headers)
    if response.text is None or response.text == "":
        return getRedirectUrl(store)

    if "hotels were found that match your search" in response.text:
        return getRedirectUrl(store)

    body = html.fromstring(response.text, "lxml")
    geoJSON = getScriptWithGeo(body)
    if geoJSON is None:
        return getRedirectUrl(store)
    return store, body, geoJSON


def getScriptWithGeo(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if '"geo":{' in script:
            return json.loads(script, strict=False)
    return None


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores found = {len(stores)}")

    count = 0
    failed = 0
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for store, body, geoJSON in executor.map(fetchSingleSore, stores):
            count = count + 1
            if count % 100 == 0:
                log.info(f"scrapped {count} pages ...")

            store_number = store["store_number"]

            if body is None or geoJSON is None:
                failed = failed + 1
                log.error(f"{count}. #failed {failed}  {store['page_url']} ...")

                page_url = store["ex_page_url"]
                urlParts = page_url.split("/")
                location_type = urlParts[len(urlParts) - 4]
                yield SgRecord(
                    locator_domain=website,
                    location_type=location_type,
                    store_number=store_number,
                    page_url=page_url,
                )
                continue

            location_name = geoJSON["name"]
            page_url = geoJSON["@id"]
            street_address = geoJSON["address"]["streetAddress"]
            city = geoJSON["address"]["addressLocality"]
            state = store["state"]
            zip_postal = MISSING
            if "postalCode" in geoJSON["address"]:
                zip_postal = geoJSON["address"]["postalCode"]

            country_code = store["countryCode"]
            phone = f" {geoJSON['telephone']}"
            latitude = f" {geoJSON['geo']['latitude']}"
            longitude = f" {geoJSON['geo']['longitude']}"

            urlParts = page_url.split("/")
            location_type = urlParts[len(urlParts) - 4]
            yield SgRecord(
                locator_domain=website,
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
            )

    log.error(f"{failed} requests failed ...")


def scrape():
    log.info("Crawling Started")
    count = 0
    start = time.time()
    results = fetchData()
    with SgWriter() as writer:
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"No of records being processed: {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
