# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "tous.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
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
    url = "https://www.tous.com/us-en/stores"
    country_list = ["US", "CA"]

    for country in country_list:
        api_res = session.get(
            f"https://brand.tous.com/us-en/stores/listByCountry.html?idBusinessCountry={country}",
            headers=headers,
        )
        json_res = json.loads(api_res.text)

        stores_list = json_res["shops"]
        for store in stores_list:
            if store["idShopType"] == "1":
                page_url = url
                locator_domain = website
                location_name = store["name"].strip()
                street_address = store["address"].strip()

                city = store["city"].strip()
                if country == "CA":
                    state = "<MISSING>"
                    zip = store["postalcode"].strip()
                if country == "US":
                    zip = store["postalcode"]
                    if zip and len(zip.strip().split(" ")) == 2:
                        zip = store["postalcode"].strip().split(" ")[1].strip()
                        state = store["postalcode"].strip().split(" ")[0].strip()
                    else:
                        zip = store["postalcode"].strip()
                        state = "<MISSING>"

                country_code = country

                store_number = store["id"]
                phone = store["phone"].strip()

                location_type = "<MISSING>"

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
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
