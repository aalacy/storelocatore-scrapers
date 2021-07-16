# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import re

website = "tiffany.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def validhour(x):
    if (
        ("AM" in x.upper() and "PM" in x.upper())
        or (re.search("\\d *[AP]M", x.upper()))
        or ("DAILY" in x.upper())
        or ("M" in x.upper() and ":" in x.upper())
        or ("TU" in x.upper() and ":" in x.upper())
        or ("WED" in x.upper() and ":" in x.upper())
        or ("TH" in x.upper() and ":" in x.upper())
        or ("F" in x.upper() and ":" in x.upper())
        or ("SA" in x.upper() and ":" in x.upper())
        or ("SU" in x.upper() and ":" in x.upper())
        or ("～" in x.upper())
        or ("-" in x.upper())
    ):

        if (
            "JAN" in x.upper()
            or "FEB" in x.upper()
            or "MAR" in x.upper()
            or "APR" in x.upper()
            or "MAY" in x.upper()
            or "JUN" in x.upper()
            or "JUL" in x.upper()
            or "AUG" in x.upper()
            or "SEP" in x.upper()
            or "OCT" in x.upper()
            or "NOV" in x.upper()
            or "DEC" in x.upper()
            or "HOLIDAY" in "".join(x.upper()[:7])  # Extra check for Holiday
            or "E-MAIL." in x.upper()
            or "E-MAIL:" in x.upper()
            or "PRIOR TO YOUR VISIT." in x.upper()
            or "IN-PERSON" in x.upper()
            or "IN-STORE" in x.upper()
        ):
            return False
        return True
    return False


def fetch_data():
    # Your scraper here
    countries_req = session.get(
        "https://www.tiffany.com/jewelry-stores/store-list/", headers=headers
    )
    countries_sel = lxml.html.fromstring(countries_req.text)
    countries = countries_sel.xpath(
        '//ul[@class="stores-filter__regions-content-dropdown-list"]/li/a/@href'
    )
    countries = list(set(countries))
    for country_url in countries:
        search_url = "https://www.tiffany.com/" + country_url

        if "/homepage/" in search_url:
            continue
        log.info(f"\n======\n{search_url}\n=======\n")

        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="store-list__store-item"]/a[@class="cta"]/@href'
        )
        for store_url in stores[:]:
            page_url = "https://www.tiffany.com" + store_url
            locator_domain = website
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zip = ""
            store_number = "<MISSING>"
            phone = ""
            location_type = "<MISSING>"
            latitude = ""
            longitude = ""
            hours_of_operation = ""

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_list:
                try:
                    if "Store" == json.loads(js)["@type"]:
                        json_data = json.loads(js)
                        location_name = json_data["name"]
                        street_address = (
                            json_data["address"]["streetAddress"]
                            .replace("Chinook Centre ,", "")
                            .strip()
                            .replace("West Edmonton Mall,", "")
                            .strip()
                            .replace(", Hato Rey", "")
                            .strip()
                            .replace(
                                "Visit our New Location at Westfield Century City,", ""
                            )
                            .strip()
                            .replace("Visit our beautifully renovated store,", "")
                            .strip()
                            .replace("Santa Monica Place,", "")
                            .strip()
                            .replace("Royal Hawaiian Center,", "")
                            .strip()
                            .replace("Northbrook Court,", "")
                            .strip()
                            .replace("The Shops at Hudson Yards,", "")
                            .strip()
                        )
                        city = json_data["address"]["addressLocality"]
                        state = json_data["address"]["addressRegion"]
                        zip = json_data["address"]["postalCode"]
                        country_code = json_data["address"]["addressCountry"]

                        try:
                            int(state)
                            state = json_data["address"]["postalCode"]  # Error in DATA
                            zip = json_data["address"]["addressRegion"]
                        except ValueError:
                            pass

                        if (
                            page_url
                            == "https://www.tiffany.com/jewelry-stores/mall-of-san-juan/"
                        ):
                            street_address = "1000 Mall of San Juan Boulevard"
                            zip = "00924"

                        phone = json_data["telephone"]
                        map_link = json_data["hasMap"]
                        location_type = json_data["brand"]
                        try:
                            latitude = (
                                map_link.split("sll=")[1].strip().split(",")[0].strip()
                            )
                            longitude = (
                                map_link.split("sll=")[1]
                                .strip()
                                .split(",")[1]
                                .strip()
                                .replace("'", "")
                                .strip()
                            )
                        except:
                            pass

                        if (
                            "permanently closed"
                            in json_data["openingHours"]
                            + " "
                            + json_data["specialOpeningHoursSpecification"]
                        ):
                            hours_of_operation = "permanently closed"
                        elif (
                            "temporarily closed"
                            in json_data["openingHours"]
                            + " "
                            + json_data["specialOpeningHoursSpecification"]
                        ):
                            hours_of_operation = "temporarily closed"
                        else:
                            temp_hours = json_data["openingHours"]
                            temp_hours = (
                                temp_hours.split("Holiday ")[0]
                                .split("urbside ")[0]
                                .split("Café Hours")[0]
                            )
                            hours = [
                                x.strip()
                                for x in list(
                                    filter(validhour, temp_hours.split("<br>"))
                                )
                            ]
                            hours_of_operation = "; ".join(hours).strip("; ").strip()
                            if not hours_of_operation:

                                temp_hours = json_data[
                                    "specialOpeningHoursSpecification"
                                ]

                                temp_hours = (
                                    temp_hours.split("Holiday ")[0]
                                    .split("urbside ")[0]
                                    .split("Café Hours")[0]
                                )
                                hours = [
                                    x.strip()
                                    for x in list(
                                        filter(validhour, temp_hours.split("<br>"))
                                    )
                                ]
                                hours_of_operation = (
                                    "; ".join(hours).strip("; ").strip()
                                )

                            hours_of_operation = (
                                hours_of_operation.replace("<b>", "")
                                .replace("<BR>", "")
                                .replace("-", " to ")
                            )
                            hours_of_operation = (
                                hours_of_operation.split("e to mail from")[1].strip()
                                if "e to mail from" in hours_of_operation
                                else hours_of_operation
                            )

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
