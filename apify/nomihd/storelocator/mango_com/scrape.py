# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mango.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "shop.mango.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        countries_req = session.get("https://mango.com/", headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath('//select[@id="countrySelect"]/option')[1:]
        for country in countries:
            country_code = "".join(country.xpath("@value")).strip()
            log.info(f"pulling info for country: {country_code}")

            search_req = session.get(
                "https://shop.mango.com/entradaPaises.faces?pais={}&idioma=US&provincia=".format(
                    country_code
                ),
                headers=headers,
            )
            if "var dataLayerV2Json = " not in search_req.text:
                log.info(
                    f"***********couldn't find data for country: {country_code} *************"
                )
                continue

            countryID = json.loads(
                search_req.text.split("var dataLayerV2Json = ")[1]
                .strip()
                .split("};")[0]
                .strip()
                + "}"
            )["shop"]["countryID"]

            search_url = "https://shop.mango.com/services/stores/locator/US/?userLogged=false&countryId={}&latitude=37.0902&longitude=-95.7129&minRadius=0&maxRadius=1500000"
            stores_req = session.get(search_url.format(countryID), headers=headers)
            stores = json.loads(stores_req.text)["stores"]
            for store_json in stores:
                page_url = "<MISSING>"
                latitude = store_json["pos"]["lat"]
                longitude = store_json["pos"]["lng"]
                if latitude == "0.0":
                    latitude = "<MISSING>"
                if longitude == "0.0":
                    longitude = "<MISSING>"

                if latitude == 0.0 or latitude == 0:
                    latitude = "<MISSING>"
                if longitude == 0.0 or longitude == 0:
                    longitude = "<MISSING>"

                location_name = store_json.get("address", "<MISSING>")

                locator_domain = website

                location_type = "<MISSING>"

                street_address = store_json.get("address", "<MISSING>")

                city = store_json.get("city", "<MISSING>")
                if "undefined" in city:
                    city = "<MISSING>"

                state = "<MISSING>"
                zip = store_json.get("postalCode", "<MISSING>")
                phone = store_json.get("tel", "<MISSING>")
                hours_of_operation = ""
                hours_list = []
                hours = store_json.get("openingHours", [])
                store_number = store_json.get("id", "<MISSING>")
                for hour in hours:
                    day = hour["day"]
                    time = ""
                    if "mOpen" in hour:
                        time = hour["mOpen"] + "-" + hour["mClose"]

                    if "aOpen" in hour:
                        if len(time) > 0:
                            time = time + ", " + hour["aOpen"] + "-" + hour["aClose"]
                        else:
                            time = hour["aOpen"] + "-" + hour["aClose"]

                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

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
