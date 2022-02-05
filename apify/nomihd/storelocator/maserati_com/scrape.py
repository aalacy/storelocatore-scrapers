# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "maserati.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.geocms.it",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-dest": "script",
    "referer": "https://www.maserati.com/international/en/shopping-tools/dealer-locator",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    (
        "parameters",
        "method_name=GetObject&callback=scube.geocms.GeoResponse.execute&id=1&query=(%5Bsales%5D%3D%5Btrue%5D%20OR%20%5Bassistance%5D%3D%5Btrue%5D%20OR%20%5BautoBodyShop%5D%3D%5Btrue%5D)&licenza=geo-maseratispa&progetto=DealerLocator&lang=ALL",
    ),
    ("encoding", "UTF-8"),
)


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://www.geocms.it/Server/servlet/S3JXServletCall",
            headers=headers,
            params=params,
        )

        stores = json.loads(
            stores_req.text.replace('\\"', '"')
            .strip()
            .split('eval(scube.geocms.GeoResponse.execute("')[1]
            .strip()
            .split('","",1));')[0]
            .strip()
        )["L"][0]["O"]
        for store in stores:
            store_number = store["pk"]
            locator_domain = website
            prop = store["U"]
            page_url = prop.get("url", "<MISSING>")
            location_name = store["D"]
            if location_name and location_name == "GHOST":
                continue
            street_address = prop.get("address", "<MISSING>")
            city = prop.get("city", "<MISSING>")
            state = prop.get("province", "<MISSING>")
            zip = prop.get("postcode", "<MISSING>")

            country_code = prop.get("countryIsoCode2", "<MISSING>")

            phone = prop.get("phone", "<MISSING>")
            if phone == "(" or phone == "1":
                phone = "<MISSING>"

            location_type = "<MISSING>"

            latitude = store["G"][0]["P"][0]["y"]
            longitude = store["G"][0]["P"][0]["x"]

            hours_list = []
            try:
                hours = prop["G"]["opening_hours"]  # mon-sun
                for hour in hours:
                    day = ""
                    if hour["giorno"] == "1":
                        day = "Monday:"
                    if hour["giorno"] == "2":
                        day = "Tuesday:"
                    if hour["giorno"] == "3":
                        day = "Wednesday:"
                    if hour["giorno"] == "4":
                        day = "Thursday:"
                    if hour["giorno"] == "5":
                        day = "Friday:"
                    if hour["giorno"] == "6":
                        day = "Saturday:"
                    if hour["giorno"] == "7":
                        day = "Sunday:"

                    am_list = []
                    pm_list = []
                    if "amFrom" in hour:
                        am_list.append(hour["amFrom"])
                    if "amTo" in hour:
                        am_list.append(hour["amTo"])

                    if "pmFrom" in hour:
                        pm_list.append(hour["pmFrom"])
                    if "pmTo" in hour:
                        pm_list.append(hour["pmTo"])

                    if len(am_list) > 0 and len(pm_list) > 0:
                        hours_list.append(
                            day + str(min(am_list)) + " - " + str(max(pm_list))
                        )

                    if len(am_list) > 0 and len(pm_list) <= 0:
                        hours_list.append(day + " - ".join(am_list))

                    if len(pm_list) > 0 and len(am_list) <= 0:
                        hours_list.append(day + " - ".join(pm_list))
            except:
                pass

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
