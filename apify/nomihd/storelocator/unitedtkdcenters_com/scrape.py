# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser
import json
from bs4 import BeautifulSoup

website = "unitedtkdcenters.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://unitedtkdcenters.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[contains(text(),"view location")]/@href')
    for store_url in stores:
        if "http" not in store_url:
            page_url = "https://unitedtkdcenters.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            soup = BeautifulSoup(store_req.text, "lxml")
            location_name = ""
            try:
                location_name = soup.find(
                    "h2", {"data-aid": "CONTACT_SECTION_TITLE_REND"}
                ).text.strip()
            except:
                location_name = soup.find(
                    "h1", {"data-aid": "CONTACT_SECTION_TITLE_REND"}
                ).text.strip()

            location_type = "<MISSING>"
            locator_domain = website

            raw_address = soup.find(
                "p", {"data-aid": "CONTACT_INFO_ADDRESS_REND"}
            ).text.strip()

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if "," in city:
                city = city.split(",")[0].strip()

            state = formatted_addr.state
            if state == "New York, New York":
                state = "NY"

            zipp = formatted_addr.postcode
            phone = soup.find("a", {"data-aid": "CONTACT_INFO_PHONE_REND"}).text.strip()
            hours_json_text = store_req.text.split(
                '@widget/CONTACT/bs-Component"},false);}(JSON.parse("'
            )[1].strip()
            hours_json = json.loads(
                hours_json_text.split('")')[0].strip().replace('\\"', '"').strip()
            )

            hours = hours_json["structuredHours"]
            hours_list = []
            for hour in hours:
                day = hour["hour"]["day"]
                if hour["hour"]["closed"] is True:
                    time = "Closed"
                else:
                    time = hour["hour"]["openTime"] + "-" + hour["hour"]["closeTime"]
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            country_code = "US"
            store_number = "<MISSING>"

            json_text = store_req.text.split(
                '@widget/CONTACT/bs-genericMap"},false);}(JSON.parse("'
            )[1].strip()
            map_json = json.loads(
                json_text.split('")')[0].strip().replace('\\"', '"').strip()
            )

            latitude = map_json["lat"]
            longitude = map_json["lon"]

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
