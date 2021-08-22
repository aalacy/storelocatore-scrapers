from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd


def scrape():
    locator_domains = []
    page_urls = []
    location_names = []
    street_addresses = []
    citys = []
    states = []
    zips = []
    country_codes = []
    store_numbers = []
    phones = []
    location_types = []
    latitudes = []
    longitudes = []
    hours_of_operations = []

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    }

    x = 0
    while True:
        x = x + 1
        url = (
            "https://www.pnfp.com/contact-us/pinnacle-locations-atms/location-search-results/?location=37901&loctype=atm&fullyreopened=&page="
            + str(x)
        )
        response = session.get(url).text
        if "We’re sorry, your search did not return any results" in response:
            break
        soup = bs(response, "html.parser")

        grids = soup.find_all("div", attrs={"class": "location-item"})

        for grid in grids:
            locator_domain = "pnfp.com"
            page_url_contenders = grid.find_all("a")

            page_url = url
            store_number = "<MISSING>"
            for a_tag in page_url_contenders:
                if "contact-us" in a_tag["href"]:
                    page_url = "https://www.pnfp.com/" + a_tag["href"]
                    store_number = page_url.split("?o=")[1]

            location_name = grid.find("h2").text.strip()

            address_parts = [
                part.strip()
                for part in grid.find("div", attrs={"class": "loc-col1"})
                .text.strip()
                .split("\n")
            ]
            address = address_parts[0]

            try:
                city = address_parts[1].split(",")[0]
                state = address_parts[1].split(", ")[1].split(" ")[0]
                zipp = address_parts[1].split(", ")[1].split(" ")[1]

            except Exception:
                address = address + " " + address_parts[1]

                city = address_parts[2].split(",")[0]
                state = address_parts[2].split(", ")[1].split(" ")[0]
                zipp = address_parts[2].split(", ")[1].split(" ")[1]

            phone = ""
            for part in address_parts:
                if (
                    bool(re.search(r"(\d\d\d)", part)) is True
                    and bool(re.search("[a-zA-Z]", part)) is False
                ):
                    phone = part

            if phone == "" and "advisor-search-results" in page_url:
                phone_response = session.get(page_url).text
                phone_soup = bs(phone_response, "html.parser")

                phone_section = phone_soup.find(
                    "div", attrs={"class": "location-item"}
                ).text.strip()

                y = 0
                phone = ""
                for character in phone_section:
                    if bool(re.search(r"\d", character)) is True:
                        y = y + 1
                        phone = phone + character
                    if y == 10:
                        break

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            try:
                hours = ""
                hours_parts = (
                    grid.find("div", attrs={"class": "loc-col2"})
                    .find("p")
                    .text.strip()
                    .split("\n")[1]
                    .strip()
                    .split("p.m.")
                )

                hours_parts_revisited = []
                for part in hours_parts:
                    if "Fri" in part:
                        hours_parts_revisited.append(part)
                        break

                    hours_parts_revisited.append(part)

                for part in hours_parts_revisited:
                    hours = hours + part + "p.m., "

                hours = hours[:-2]

            except Exception:
                hours = "<MISSING>"

            if "mon" not in hours[:4].lower():
                hours = "<MISSING>"

            country_code = "US"

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(location_name)
            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            country_codes.append(country_code)
            store_numbers.append(store_number)
            phones.append(phone)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)

    df_atm = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": location_names,
            "street_address": street_addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "store_number": store_numbers,
            "phone": phones,
            "latitude": latitudes,
            "longitude": longitudes,
            "hours_of_operation": hours_of_operations,
            "country_code": country_codes,
        }
    )

    locator_domains = []
    page_urls = []
    location_names = []
    street_addresses = []
    citys = []
    states = []
    zips = []
    country_codes = []
    store_numbers = []
    phones = []
    location_types = []
    latitudes = []
    longitudes = []
    hours_of_operations = []

    x = 0
    while True:
        x = x + 1
        url = (
            "https://www.pnfp.com/contact-us/pinnacle-locations-atms/location-search-results/?location=37901&loctype=office&fullyreopened=&page="
            + str(x)
        )
        response = session.get(url).text
        if "We’re sorry, your search did not return any results" in response:
            break
        soup = bs(response, "html.parser")

        grids = soup.find_all("div", attrs={"class": "location-item"})

        for grid in grids:
            locator_domain = "pnfp.com"
            page_url_contenders = grid.find_all("a")

            page_url = url
            store_number = "<MISSING>"
            for a_tag in page_url_contenders:
                if "contact-us" in a_tag["href"]:
                    page_url = "https://www.pnfp.com/" + a_tag["href"]
                    store_number = page_url.split("?o=")[1]

            location_name = grid.find("h2").text.strip()

            address_parts = [
                part.strip()
                for part in grid.find("div", attrs={"class": "loc-col1"})
                .text.strip()
                .split("\n")
            ]
            address = address_parts[0]

            try:
                city = address_parts[1].split(",")[0]
                state = address_parts[1].split(", ")[1].split(" ")[0]
                zipp = address_parts[1].split(", ")[1].split(" ")[1]

            except Exception:
                address = address + " " + address_parts[1]

                city = address_parts[2].split(",")[0]
                state = address_parts[2].split(", ")[1].split(" ")[0]
                zipp = address_parts[2].split(", ")[1].split(" ")[1]

            phone = ""
            for part in address_parts:
                if (
                    bool(re.search(r"(\d\d\d)", part)) is True
                    and bool(re.search("[a-zA-Z]", part)) is False
                ):
                    phone = part

            if phone == "" and "advisor-search-results" in page_url:
                phone_response = session.get(page_url).text
                phone_soup = bs(phone_response, "html.parser")

                phone_section = phone_soup.find(
                    "div", attrs={"class": "location-item"}
                ).text.strip()

                y = 0
                phone = ""
                for character in phone_section:
                    if bool(re.search(r"\d", character)) is True:
                        y = y + 1
                        phone = phone + character
                    if y == 10:
                        break

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            try:
                hours = ""
                hours_parts = (
                    grid.find("div", attrs={"class": "loc-col2"})
                    .find("p")
                    .text.strip()
                    .split("\n")[1]
                    .strip()
                    .split("p.m.")
                )

                hours_parts_revisited = []
                for part in hours_parts:
                    if "Fri" in part:
                        hours_parts_revisited.append(part)
                        break

                    hours_parts_revisited.append(part)

                for part in hours_parts_revisited:
                    hours = hours + part + "p.m., "

                hours = hours[:-2]

            except Exception:
                hours = "<MISSING>"

            country_code = "US"

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(location_name)
            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            country_codes.append(country_code)
            store_numbers.append(store_number)
            phones.append(phone)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)

    df_office = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": location_names,
            "street_address": street_addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "store_number": store_numbers,
            "phone": phones,
            "latitude": latitudes,
            "longitude": longitudes,
            "hours_of_operation": hours_of_operations,
            "country_code": country_codes,
        }
    )

    locator_domains = []
    page_urls = []
    location_names = []
    street_addresses = []
    citys = []
    states = []
    zips = []
    country_codes = []
    store_numbers = []
    phones = []
    location_types = []
    latitudes = []
    longitudes = []
    hours_of_operations = []

    x = 0
    while True:
        x = x + 1
        url = (
            "https://www.pnfp.com/contact-us/pinnacle-locations-atms/location-search-results/?location=37901&loctype=&fullyreopened=&page="
            + str(x)
        )
        response = session.get(url, headers=headers).text
        if "We’re sorry, your search did not return any results" in response:
            break
        soup = bs(response, "html.parser")

        grids = soup.find_all("div", attrs={"class": "location-item"})

        for grid in grids:
            locator_domain = "pnfp.com"
            page_url_contenders = grid.find_all("a")

            page_url = url
            store_number = "<MISSING>"
            for a_tag in page_url_contenders:
                if "contact-us" in a_tag["href"]:
                    page_url = "https://www.pnfp.com/" + a_tag["href"]
                    store_number = page_url.split("?o=")[1]

            location_name = grid.find("h2").text.strip()

            address_parts = [
                part.strip()
                for part in grid.find("div", attrs={"class": "loc-col1"})
                .text.strip()
                .split("\n")
            ]
            address = address_parts[0]

            try:
                city = address_parts[1].split(",")[0]
                state = address_parts[1].split(", ")[1].split(" ")[0]
                zipp = address_parts[1].split(", ")[1].split(" ")[1]

            except Exception:
                address = address + " " + address_parts[1]

                city = address_parts[2].split(",")[0]
                state = address_parts[2].split(", ")[1].split(" ")[0]
                zipp = address_parts[2].split(", ")[1].split(" ")[1]

            phone = ""
            for part in address_parts:
                if (
                    bool(re.search(r"(\d\d\d)", part)) is True
                    and bool(re.search("[a-zA-Z]", part)) is False
                ):
                    phone = part

            if phone == "" and "advisor-search-results" in page_url:
                phone_response = session.get(page_url).text
                phone_soup = bs(phone_response, "html.parser")

                phone_section = phone_soup.find(
                    "div", attrs={"class": "location-item"}
                ).text.strip()

                y = 0
                phone = ""
                for character in phone_section:
                    if bool(re.search(r"\d", character)) is True:
                        y = y + 1
                        phone = phone + character
                    if y == 10:
                        break

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            try:
                hours = ""
                hours_parts = (
                    grid.find("div", attrs={"class": "loc-col2"})
                    .find("p")
                    .text.strip()
                    .split("\n")[1]
                    .strip()
                    .split("p.m.")
                )

                hours_parts_revisited = []
                for part in hours_parts:
                    if "Fri" in part:
                        hours_parts_revisited.append(part)
                        break

                    hours_parts_revisited.append(part)

                for part in hours_parts_revisited:
                    hours = hours + part + "p.m., "

                hours = hours[:-2]

            except Exception:
                hours = "<MISSING>"

            country_code = "US"

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(location_name)
            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            country_codes.append(country_code)
            store_numbers.append(store_number)
            phones.append(phone)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)

    df_missing = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": location_names,
            "street_address": street_addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "store_number": store_numbers,
            "phone": phones,
            "latitude": latitudes,
            "longitude": longitudes,
            "hours_of_operation": hours_of_operations,
            "country_code": country_codes,
        }
    )

    atm_office_df = pd.DataFrame()

    office_rows = []
    for row in df_office.iterrows():
        office_rows.append(
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
        )

    x = 0
    for row in df_atm.iterrows():
        atm_office_df = atm_office_df.append(row[1])
        if (
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
            in office_rows
        ):
            location_types.append("office and atm")
        else:
            location_types.append("atm")

    atm_rows = []
    for row in df_atm.iterrows():
        atm_rows.append(
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
        )

    x = 0
    for row in df_office.iterrows():
        atm_office_df = atm_office_df.append(row[1])
        if (
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
            in atm_rows
        ):
            location_types.append("office and atm")
        else:
            location_types.append("office")

    atm_office_rows = []
    for row in atm_office_df.iterrows():
        atm_office_rows.append(
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
        )

    x = 0
    for row in df_missing.iterrows():
        if (
            row[1]["location_name"]
            + row[1]["store_number"]
            + row[1]["street_address"]
            + row[1]["zip"]
            in atm_office_rows
        ):
            pass
        else:
            atm_office_df = atm_office_df.append(row[1])
            location_types.append("<MISSING>")

    atm_office_df["location_type"] = location_types

    df = atm_office_df
    df = df.fillna("<MISSING>")
    df = df.replace(r"^\s*$", "<MISSING>", regex=True)

    df["dupecheck"] = (
        df["location_name"]
        + df["street_address"]
        + df["city"]
        + df["state"]
        + df["location_type"]
    )

    df = df.drop_duplicates(subset=["dupecheck"])
    df = df.drop(columns=["dupecheck"])
    df = df.replace(r"^\s*$", "<MISSING>", regex=True)
    df = df.fillna("<MISSING>")

    df = df.reset_index(drop=True)

    for x in range(len(hours_of_operations)):
        hours_value = df.at[x, "hours_of_operation"]
        if "office" in hours_value.lower():
            df.at[x, "hours_of_operation"] = "<MISSING>"
            df.at[x, "location_type"] = "loan office"

    df.to_csv("data.csv", index=False)


scrape()
