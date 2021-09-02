from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = SgLogSetup().get_logger("purolator_com")
session = SgRequests()


def fetch_data():
    base_url = "purolator.com"
    headers = {
        "authority": "api.purolator.com",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "application/vnd.puro.locator+json",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "origin": "https://www.purolator.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.purolator.com/",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    params = (
        ("radialDistanceInKM", "7000"),
        ("maxNumberofLocations", "1000"),
        ("locationType", ["ShippingCentre"]),
    )

    r = session.get(
        "https://api.purolator.com/locator/puro/json/location/byCoordinates/45.535785/-73.667562",
        headers=headers,
        params=params,
    ).json()

    k = r["locations"]
    for i in k:
        phone = i["phoneNumber"]
        location_name = i["locationName"]
        location_type = i["locationType"]
        address = (
            i["address"]["streetNumber"]
            + " "
            + i["address"]["streetName"]
            + " "
            + i["address"]["streetType"]
        )
        latitude = i["latitude"]
        longitude = i["longitude"]
        city = i["address"]["municipalityName"]
        country_code = i["address"]["countryCode"]
        zip = i["address"]["postalCode"]
        state = i["address"]["provinceCode"]
        hours = i["hoursOfOperation"]
        store_number = i["locationId"]
        hours_list = []
        for i in hours:
            hours_list.append(i["day"] + ": " + i["open"] + "-" + i["close"])

        hours_of_operation = "; ".join(hours_list).strip()
        yield SgRecord(
            locator_domain=base_url,
            page_url="<MISSING>",
            location_name=location_name,
            street_address=address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
