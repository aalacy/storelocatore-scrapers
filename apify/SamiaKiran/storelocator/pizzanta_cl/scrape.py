import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "pizzanta_cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)


api_url = "https://api.getjusto.com/graphql?operationName=getWebsitePage_cached"


headers = {
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.pizzanta.cl",
    "referer": "https://www.pizzanta.cl/",
    "accept-language": "en-US,en;q=0.9",
}

DOMAIN = "https://pizzanta.cl/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.pizzanta.cl/locales"
        log.info("Fetching Page and Website Id's....")
        r = session.get(url, headers=headers)
        page_id = r.text.split('"path":"/"},{"_id":"')[1].split('"')[0]
        website_id = r.text.split('{"website":{"_id":"')[1].split('"')[0]
        payload = json.dumps(
            {
                "operationName": "getWebsitePage_cached",
                "variables": {"pageId": page_id, "websiteId": website_id},
                "query": "query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\n  page(pageId: $pageId, websiteId: $websiteId) {\n    _id\n    path\n    activeComponents {\n      _id\n      options\n      componentTypeId\n      schedule {\n        isScheduled\n        latestScheduleStatus\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            }
        )
        loclist = session.post(api_url, headers=headers, data=payload).json()["data"][
            "page"
        ]["activeComponents"][1]["options"]["stores"]
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            try:
                phone = loc["phone"]
            except:
                phone = MISSING
            log.info(location_name)
            place_id = loc["placeId"]
            hours_of_operation = loc["otherText"]
            address_url = (
                "https://api.getjusto.com/graphql?operationName=getPlaceDetails_cached"
            )
            payload = json.dumps(
                {
                    "operationName": "getPlaceDetails_cached",
                    "variables": {"placeId": place_id},
                    "query": "query getPlaceDetails_cached($placeId: ID) {\n  place(placeId: $placeId) {\n    _id\n    text\n    secondaryText\n    location\n    __typename\n  }\n}\n",
                }
            )
            log.info(f"Fetching address details for {location_name}")
            temp = session.post(address_url, headers=headers, data=payload).json()[
                "data"
            ]["place"]
            raw_address = strip_accents(temp["text"] + " " + temp["secondaryText"])
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            coords = temp["location"]
            latitude = coords["lat"]
            longitude = coords["lng"]
            country_code = "Chile"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.pizzanta.cl/locales",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
