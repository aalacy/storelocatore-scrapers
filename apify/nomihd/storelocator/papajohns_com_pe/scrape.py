# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "papajohns.com.pe"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}

api_headers = {
    "authority": "4231ficvsl.execute-api.us-east-1.amazonaws.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "x-api-key": "Vl1YfpARKUaAh9hF7oszCaovoQMKIBzs7kOUSmce",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://papajohns.com.pe",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://papajohns.com.pe/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    home_url = "https://papajohns.com.pe/locales"
    with SgRequests() as session:
        home_req = session.get(home_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)

        token = (
            home_req.headers["Set-Cookie"]
            .split("tokenSession=")[1]
            .strip()
            .split(";")[0]
            .strip()
        )

        cities = home_sel.xpath('//select[@id="gender"]/option[position()>2]/@value')
        for cty in cities:
            data = {"tag": cty, "section": "locales", "session_token": token}

            search_res = session.post(
                "https://4231ficvsl.execute-api.us-east-1.amazonaws.com/pro/api/stores/tag",
                headers=api_headers,
                data=json.dumps(data),
            )

            store_list = json.loads(search_res.text)["data"]["stores"]

            for store in store_list:

                page_url = home_url

                locator_domain = website
                location_name = store["name"]

                raw_address = store["address"]

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = cty
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = "PE"

                store_number = store["storelocator_id"]
                phone = store["phone"]
                if phone == "-":
                    phone = "<MISSING>"

                phone = (
                    phone.replace("Food Court", "")
                    .strip()
                    .replace("pick up", "")
                    .strip()
                )
                location_type = "<MISSING>"
                hours_list = []
                hours_sel = lxml.html.fromstring(store["description"])
                hours = hours_sel.xpath("//p/text()")
                for hour in hours:
                    hours_list.append("".join(hour).strip())

                hours_of_operation = "; ".join(hours_list).strip()
                latitude = store["latitude"]
                longitude = store["longtitude"]
                if latitude == "0.000":
                    latitude = "<MISSING>"
                if longitude == "0.000":
                    longitude = "<MISSING>"

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
