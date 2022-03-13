# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    search_url = "https://www.bathandbodyworks.in/store-locator"
    headers = {
        "authority": "www.bathandbodyworks.in",
        "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "origin": "https://www.bathandbodyworks.in",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.bathandbodyworks.in/store-locator",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    params = (("route", "extension/module/wk_store_locater/setter"),)

    data = {
        "longitude": "0",
        "latitude": "0",
        "city": "all",
        "location": "Name of Town or City",
    }

    with SgRequests() as session:
        search_res = session.post(
            "https://www.bathandbodyworks.in/index.php",
            headers=headers,
            params=params,
            data=data,
        )
        log.info(search_res)
        stores = search_res.text.split("~")
        for index in range(0, len(stores) - 1):
            store_info = stores[index].split("!")
            page_url = search_url

            locator_domain = website

            location_name = store_info[3].strip()

            raw_address = (
                stores[index]
                .split("!!!")[-1]
                .strip()
                .replace("\\/", "/")
                .strip()
                .split("PH -")[0]
                .strip()
                .split("; Contact-")[0]
                .strip()
                .replace("\\u2013", "-")
                .strip()
                .split("; contact -")[0]
                .strip()
                .replace("\\n", "")
                .strip()
                .split("Email:")[0]
                .strip()
                .split(", INDIA")[0]
                .strip()
            )
            if raw_address[-1] == ",":
                raw_address = "".join(raw_address[:-1]).strip()

            street_address = ", ".join(raw_address.split(",")[:-1]).strip()
            city = (
                raw_address.split(",")[-1]
                .strip()
                .replace(
                    "Chandigarh Industrial Area (Near centra mall) Phase", "Chandigarh"
                )
                .strip()
            )
            try:
                city = city.split("-")[0].strip()
            except:
                pass
            state = "<MISSING>"
            zip = "<MISSING>"
            try:
                if "Pincode" in raw_address:
                    city = city.split("Pincode")[0].strip()
                    zip = raw_address.split("Pincode")[1].strip()
                else:
                    zip = raw_address.rsplit("-", 1)[-1].strip()
            except:
                pass

            if not zip.isdigit():
                zip = "<MISSING>"

            if city == "Shop No":
                street_address = (
                    "Shop No - G 14 15 L2 Lower ground floor Hi-tech city opp to I Labs"
                )
                city = "Hyderabad"

            if city == "Infinity 2 Link RD Malad(W) Mumbai":
                street_address = "F-118, Infinity 2 Link RD Malad(W)"
                city = "Mumbai"

            try:
                if city.split(" ")[-1].isdigit():
                    zip = city.split(" ")[-1]
                    city = " ".join(city.split(" ")[:-1]).strip()
            except:
                pass
            country_code = "IN"

            store_number = store_info[0].strip().replace('"', "").strip()
            phone = "<MISSING>"
            try:
                phone = (
                    stores[index]
                    .split("!!!")[-1]
                    .strip()
                    .replace("\\/", "/")
                    .strip()
                    .split("PH -")[1]
                    .strip()
                )
            except:
                try:
                    phone = (
                        stores[index]
                        .split("!!!")[-1]
                        .strip()
                        .replace("\\/", "/")
                        .strip()
                        .split("; Contact-")[1]
                        .strip()
                    )
                except:
                    try:
                        phone = (
                            stores[index]
                            .split("!!!")[-1]
                            .strip()
                            .replace("\\/", "/")
                            .strip()
                            .split("; contact -")[1]
                            .strip()
                        )
                    except:
                        pass

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude, longitude = store_info[1].strip(), store_info[2].strip()

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
