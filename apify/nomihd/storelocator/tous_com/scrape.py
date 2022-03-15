# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "tous.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "brand.tous.com",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "origin": "https://www.tous.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.tous.com/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        countries_req = session.get(
            "https://www.tous.com/us-en/stores", headers=headers
        )
        countries = (
            countries_req.text.split("countries:[{")[-1]
            .strip()
            .split(",center:")[0]
            .strip()
            .split('isoCode:"')[1:]
        )
        country_list = ["US}"] + countries
        for country in country_list:
            country_code = country.split("}")[0].strip().replace('"', "").strip()
            log.info(f"pulling stores of {country_code}")
            api_res = session.get(
                f"https://brand.tous.com/us-en/stores/listByCountry.html?idBusinessCountry={country_code}",
                headers=headers,
            )
            if isinstance(api_res, SgRequestError):
                continue
            json_res = json.loads(api_res.text)

            stores_list = json_res["shops"]
            for store in stores_list:
                location_type = "<MISSING>"

                if store["idShopType"] == "1":
                    location_type = "TOUS Store"
                elif store["idShopType"] == "2":
                    location_type = "Point of sale"

                page_url = "https://www.tous.com/us-en/stores/view/" + store["id"]
                locator_domain = website
                location_name = store["name"].strip()
                street_address = store["address"].strip()
                city = store["city"].strip()
                zip = "<MISSING>"
                state = "<MISSING>"
                if country_code == "CA":
                    state = "<MISSING>"
                    zip = store["postalcode"].strip()
                if country_code == "US":
                    zip = store["postalcode"]
                    if zip and len(zip.strip().split(" ")) == 2:
                        zip = store["postalcode"].strip().split(" ")[1].strip()
                        state = store["postalcode"].strip().split(" ")[0].strip()
                    else:
                        zip = store["postalcode"].strip()
                        state = "<MISSING>"

                street_address = street_address.replace("Merrick Park,", "").strip()
                if (
                    street_address
                    == "5757 Wayne Newton Blvd, Las Vegas, NV 89119, EE. UU."
                ):
                    street_address = street_address.replace(
                        ", Las Vegas, NV 89119, EE. UU.", ""
                    ).strip()
                    state = "NV"

                if "Richmond BC" == city:
                    city = "Richmond"
                    state = "BC"

                raw_address = street_address
                if len(city) > 0 and city != "<MISSING>":
                    raw_address = raw_address + ", " + city
                if len(state) > 0 and state != "<MISSING>":
                    raw_address = raw_address + ", " + state
                if len(zip) > 0 and zip != "<MISSING>":
                    raw_address = raw_address + ", " + zip

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                store_number = store["id"]
                phone = store["phone"]
                if phone:
                    phone = phone.strip()

                hours_of_operation = store["schedule"]

                latitude = store["coordinates"]["latitude"]
                longitude = store["coordinates"]["longitude"]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
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
                    raw_address=raw_address,
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
