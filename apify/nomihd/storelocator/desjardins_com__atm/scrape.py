# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "desjardins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Origin": "https://www.desjardins.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.desjardins.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://pservices.desjardins.com/proxy/001/index_ps_en.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["entrees"]
    for store in stores:
        store_number = store["id"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        page_url = "https://www.desjardins.com/ca/your-caisse/address/index.jsp?transit={}{}".format(
            store["inst"], store["transit"]
        )

        log.info(f"Pulling data for ID: {store_number}")
        store_req = session.get(
            "https://pservices.desjardins.com/caisses/donnees_caisses.nsf/traitement?Open&ic=details&l=en&id="
            + store_number,
            headers=headers,
        )

        try:
            store_json = json.loads(
                store_req.text.replace(",,,,", "").strip().replace(",,", ",").strip()
            )["entrees"][0]["info_caisse"]

            location_name = store_json["nom"]

            locator_domain = website

            location_type = "<MISSING>"
            if store["type"] == "3":
                location_type = "ATM"

            street_address = store_json["adr"]
            city = store_json["ville"]
            state = store_json["prov"]
            zip = store_json["cp"][:3] + " " + store_json["cp"][3:]
            phone = store_json["tel"]
            hours_of_operation = ""
            hours_list = []
            try:
                hours = json.loads(store_req.text)["entrees"][0]["heures_ouverture"][
                    "services"
                ][0]["jours"]
                for hour in hours:
                    day = ""
                    time = ""
                    if hour["jour"] == "1":
                        day = "Sunday:"
                    if hour["jour"] == "2":
                        day = "Monday:"
                    if hour["jour"] == "3":
                        day = "Tuesday:"
                    if hour["jour"] == "4":
                        day = "Wednesday:"
                    if hour["jour"] == "5":
                        day = "Thursday:"
                    if hour["jour"] == "6":
                        day = "Friday:"
                    if hour["jour"] == "7":
                        day = "Saturday:"

                    if len(hour["plages"]) > 0:
                        time = hour["plages"][0]["de"] + "-" + hour["plages"][0]["a"]
                    else:
                        time = "Closed"

                    hours_list.append(day + time)

            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()

            country_code = "CA"
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

        except:
            pass


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
