#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:43:29 2019
@author: srek
"""

from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jimmychoo_com")


def fetch_data():
    url = "https://row.jimmychoo.com/en/store-locator#address=United+States&format=ajax&country=US"

    states_list_1 = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    states_list_2 = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "conneticut",
        "deleware",
        "district of columbia",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "lousiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippo",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming",
    ]
    driver = SgSelenium().chrome()
    driver.get(url)
    data = []

    soup = BeautifulSoup(driver.page_source)

    store_info = soup.find_all("div", attrs={"class": "store-infomation clearfix"})

    locator_domain = url

    for sl in range(len(store_info)):
        logger.info(sl)
        location_name = (
            store_info[sl]
            .find("div", attrs={"class": "store-name"})
            .text.replace("\n", "")
        )

        page_link = "https://row.jimmychoo.com" + store_info[sl].find(
            "div", attrs={"class": "store-name"}
        ).find("a").get("href")

        driver.get(page_link)
        time.sleep(5)

        soup_1 = BeautifulSoup(driver.page_source)

        try:
            store_type = ";".join(
                soup_1.find("div", attrs={"class": "store-types"}).text.split("\n")[
                    1:-1
                ]
            )
        except:
            store_type = "<MISSING>"

        address = list(
            filter(
                None,
                soup_1.find("div", attrs={"class": "js-store-address"}).text.split(
                    "\n"
                ),
            )
        )

        if address[-1] == "United States":
            address.remove(address[-1])
        try:
            zipcode = address[-1]
            address.remove(address[-1])
        except:
            zipcode = "<MISSING>"

        try:
            if address[-1] in states_list_1:
                state = address[-1]
                address.remove(address[-1])
            elif address[-1].lower() in states_list_2:
                state = address[-1]
                address.remove(state)
            else:
                state = "<MISSING>"
        except:
            state = "<MISSING>"
            city = "<MISSING>"
            street_address = "<MISSING>"

        if len(address) == 2:
            city = address[1]
            street_address = address[0]
        elif len(address) == 1:
            city = "<MISSING>"
            street_address = address[0]
        else:
            try:
                city = address[-1]
            except:
                city = "<MISSING>"
            try:
                street_address = ",".join(address[:-1])
            except:
                street_address = "<MISSING>"
        if "," in street_address:
            street_address = street_address.split(",")
            if len(re.findall(r"\d", street_address[0])) == 0:
                del street_address[0]
            street_address = ",".join(street_address)

        phone = soup_1.find("span", attrs={"class": "cs-option-text"}).text

        if phone == "Get Directions":
            phone = "<MISSING>"
        elif len(phone) == 0:
            phone = "<MISSING>"
        elif "email" in phone.lower():
            phone = "<MISSING>"

        try:
            hours_of_open = ":".join(
                list(
                    filter(
                        None,
                        soup_1.find("div", attrs={"class": "store-hours"}).text.split(
                            "\n"
                        ),
                    )
                )
            )
        except:
            hours_of_open = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        country_code = "US"
        data_record = {}
        data_record["locator_domain"] = locator_domain
        data_record["location_name"] = location_name.replace("’", "'").replace("–", "-")
        data_record["street_address"] = street_address.replace("’", "'").replace(
            "–", "-"
        )
        data_record["city"] = city.replace("’", "'").replace("–", "-")
        data_record["state"] = state.replace("’", "'").replace("–", "-")
        data_record["zip"] = zipcode.replace("’", "'").replace("–", "-")
        data_record["country_code"] = country_code
        data_record["store_number"] = "<MISSING>"
        data_record["phone"] = phone
        data_record["location_type"] = store_type.replace("’", "'").replace("–", "-")
        data_record["latitude"] = latitude
        data_record["longitude"] = longitude
        data_record["hours_of_operation"] = hours_of_open.replace("’", "'").replace(
            "–", "-"
        )
        data.append(data_record)

    return data


def write_output(data):
    df_data = pd.DataFrame(
        columns=[
            "locator_domain",
            "location_name",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "store_number",
            "phone",
            "location_type",
            "latitude",
            "longitude",
            "hours_of_operation",
        ]
    )

    for d in range(len(data)):
        df = pd.DataFrame(list(data[d].values())).transpose()
        df.columns = list((data[d].keys()))
        df_data = df_data.append(df)
    df_data = df_data.replace(r"^\s*$", "<MISSING>", regex=True)
    df_data = df_data.drop_duplicates(["location_name", "street_address"])
    df_data["zip"] = df_data.zip.astype(str)
    df_data.to_csv("./data.csv", index=0, header=True)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
