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
website = "pollostop_cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "content-type": "application/json",
}

DOMAIN = "https://pollostop.cl/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.pollostop.cl/locales"
        r = session.get(url, headers=headers)
        website_id = r.text.split('{"website":{"_id":"')[1].split('"')[0]
        api_url = (
            url
        ) = "https://api.getjusto.com/graphql?operationName=getWebsitePage_cached"
        payload = json.dumps(
            {
                "operationName": "getStoresZones",
                "variables": {"websiteId": website_id},
                "query": "query getStoresZones($websiteId: ID) {\n  stores(websiteId: $websiteId) {\n    items {\n      _id\n      name\n      phone\n      humanSchedule {\n        days\n        schedule\n        __typename\n      }\n      acceptDelivery\n      acceptGo\n      zones {\n        _id\n        deliveryLimits\n        __typename\n      }\n      address {\n        placeId\n        location\n        address\n        addressSecondary\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            }
        )
        loclist = session.post(api_url, headers=headers, data=payload).json()["data"][
            "stores"
        ]["items"]
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            phone = loc["phone"]
            log.info(location_name)
            temp = loc["address"]
            raw_address = strip_accents(
                temp["address"] + " " + temp["addressSecondary"]
            )
            if not loc["humanSchedule"]:
                hours_of_operation = MISSING
            else:
                hours_of_operation = ""
                hour_list = loc["humanSchedule"]
                for hour in hour_list:
                    day = hour["days"]
                    time = hour["schedule"]
                    hours_of_operation = (
                        hours_of_operation + " " + strip_accents(day) + " " + time
                    )
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
                page_url="https://www.pollostop.cl/locales",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
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
