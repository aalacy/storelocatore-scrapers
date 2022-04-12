from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("lincoln_com")
session = SgRequests(dont_retry_status_codes=([404]))
headers = {
    "authority": "www.lincoln.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "application-id": "07152898-698b-456e-be56-d3d83011d0a6",
    "x-dtreferer": "https://www.lincoln.com/dealerships/?gnav=header-finddealer",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.lincoln.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():

    base_url = "https://www.lincoln.com"
    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
    )
    for zip_code in zipcodes:
        str_zip = str(zip_code)
        logger.info(f"fetching records for zipcode:{str_zip}")
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        phone = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        get_u = (
            "https://www.lincoln.com/cxservices/dealer/Dealers.json?make=Lincoln&radius=500&filter=&minDealers=1&maxDealers=100&postalCode="
            + str_zip
        )
        try:
            k = session.get(get_u, headers=headers).json()
        except:
            continue
        if "Response" in k and "Dealer" in k["Response"]:
            if isinstance(k["Response"]["Dealer"], list):
                for i in k["Response"]["Dealer"]:
                    if i["ldlrcalltrk_lad"]:
                        phone = i["ldlrcalltrk_lad"]
                    else:
                        phone = i["Phone"]
                    if "Street1" in i["Address"]:
                        street_address = i["Address"]["Street1"]
                    else:
                        street_address = "<MISSING>"
                    city = i["Address"]["City"]
                    state = i["Address"]["State"]
                    zipp = i["Address"]["PostalCode"]
                    hours_list = []
                    if "Day" in i["SalesHours"]:
                        for j in i["SalesHours"]["Day"]:
                            if "closed" in j and j == "true":
                                hours_list.append(j["name"] + ":" + "closed")
                            elif "open" in j:
                                hours_list.append(
                                    j["name"] + ":" + j["open"] + " - " + j["close"]
                                )

                    hours_of_operation = "; ".join(hours_list).strip()
                    latitude = i["Latitude"]
                    longitude = i["Longitude"]
                    zipcodes.found_location_at(latitude, longitude)
                    location_name = i["Name"]
                    page_url = (
                        "https://www.lincoln.com/dealerships/dealer-details/"
                        + i["urlKey"]
                    )

                    yield SgRecord(
                        locator_domain=base_url,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code="US",
                        store_number="<MISSING>",
                        phone=phone,
                        location_type="<MISSING>",
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )

        if "Response" in k and "Dealer" in k["Response"]:
            if isinstance(k["Response"]["Dealer"], dict):

                if "Street1" in k["Response"]["Dealer"]["Address"]:
                    street_address = k["Response"]["Dealer"]["Address"]["Street1"]
                else:
                    street_address = "<MISSING>"

                if k["Response"]["Dealer"]["ldlrcalltrk_lad"]:
                    phone = k["Response"]["Dealer"]["ldlrcalltrk_lad"]
                else:
                    phone = k["Response"]["Dealer"]["Phone"]

                city = k["Response"]["Dealer"]["Address"]["City"]
                state = k["Response"]["Dealer"]["Address"]["State"]
                zipp = k["Response"]["Dealer"]["Address"]["PostalCode"]
                hours_list = []
                if "Day" in k["Response"]["Dealer"]["SalesHours"]:
                    for j in k["Response"]["Dealer"]["SalesHours"]["Day"]:
                        if "closed" in j and j == "true":
                            hours_list.append(j["name"] + ":" + "closed")
                        elif "open" in j:
                            hours_list.append(
                                j["name"] + ":" + j["open"] + " - " + j["close"]
                            )

                if len(hours_list) <= 0:
                    if "Day" in k["Response"]["Dealer"]["ServiceHours"]:
                        for j in k["Response"]["Dealer"]["ServiceHours"]["Day"]:
                            if "closed" in j and j == "true":
                                hours_list.append(j["name"] + ":" + "closed")
                            elif "open" in j:
                                hours_list.append(
                                    j["name"] + ":" + j["open"] + " - " + j["close"]
                                )

                hours_of_operation = "; ".join(hours_list).strip()
                latitude = k["Response"]["Dealer"]["Latitude"]
                longitude = k["Response"]["Dealer"]["Longitude"]
                zipcodes.found_location_at(latitude, longitude)
                location_name = k["Response"]["Dealer"]["Name"]
                hours_of_operation = hours_of_operation.replace(
                    " SalesHours  ServiceHours ", "<MISSING>"
                )
                page_url = (
                    "https://www.lincoln.com/dealerships/dealer-details/"
                    + k["Response"]["Dealer"]["urlKey"]
                )

                yield SgRecord(
                    locator_domain=base_url,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.ZIP,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
