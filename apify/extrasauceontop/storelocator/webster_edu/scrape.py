from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

session = SgRequests()

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

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def getdata():
    response = session.get(
        "https://www.webster.edu/_resources/dmc/php/locations.php?datasource=locations&type=listing&returntype=json&xpath=items%2Fitem&items_per_page=100&page=1&search_phrase=&isinternational%5B%5D=United%20States",
        headers=headers,
    ).json()

    locations = response["items"]

    x = 0
    for location in locations:

        locator_domain = "https://webster.edu"
        page_url = locator_domain + location["link"]
        location_name = location["name"]
        city = location["city"]
        state = location["stateprovince"]
        country_code = location["country"]
        store_number = location["code"]

        if country_code == "United States":
            country_code = "US"

        hours = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        data_loc = session.get(page_url, headers=headers).text
        soup = bs(data_loc, "html.parser")

        if x == 0:
            address_parts = soup.find_all("li", attrs={"class": "footer-address-item"})
            phone = address_parts[0].text.strip()
            address = address_parts[1].text.strip()
            zipp_part = address_parts[2].text.strip()

            zipp = re.search(r"\d\d\d\d\d", zipp_part).group(0)

            x = x + 1
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
            location_types.append(location_type)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)
            continue

        if page_url == "https://webster.edu/locations/colorado-springs/":
            address = "<MISSING>"
            zipp = "<MISSING>"
            phone = "<MISSING>"
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
            location_types.append(location_type)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)
            continue

        try:
            address_part_soup = soup.find_all(
                "div", attrs={"class": "card-accordion-body"}
            )[-1]
            address_part = str(address_part_soup)

            result = re.search(r"\d(.*)<br/>", address_part)

            maybe_address = result.group(0)

            address_pieces = maybe_address.split("<br/>")
            if len(address_pieces) > 2:
                address_pieces.pop(-1)

                zipp_check = address_pieces[-1].split(" ")[-1]
                m = re.search(r"\d+$", zipp_check)

                if m is None:
                    address = ""
                    for piece in address_pieces:
                        address = address + piece + " "
                    address = address[:-1]

                    zipp = re.search(r"\d\d\d\d\d", address_part).group(0)

                else:

                    address_pieces.pop(-1)

                    address = ""
                    for piece in address_pieces:
                        address = address + piece + " "
                    address = address[:-1]

                    zipp = zipp_check

                p_tags = address_part_soup.find_all("p")
                for tag in p_tags:
                    if "Phone" in tag.text.strip():
                        phone_text = tag.text.strip().split("Phone")[1]
                        y = 0
                        phone = ""
                        for character in phone_text:
                            m = re.search(r"\d", character)
                            if m is not None:
                                phone = phone + character
                                y = y + 1

                            if y == 10:
                                break

                        break
            else:

                p_tags = address_part_soup.find_all("p")

                address = ""
                for tag in p_tags:
                    if "Phone" in tag.text.strip():
                        zipp = tag.text.strip().split("Phone")[0].split(" ")[-1]

                        phone_text = tag.text.strip().split("Phone")[1]
                        y = 0
                        phone = ""
                        for character in phone_text:
                            m = re.search(r"\d", character)
                            if m is not None:
                                phone = phone + character
                                y = y + 1

                            if y == 10:
                                break

                        break
                    else:
                        address = address + tag.text.strip() + " "
                address = address[:-1]

        except IndexError:
            address = "<MISSING>"
            zipp = "<MISSING>"
            phone = "<MISSING>"

        except AttributeError:

            address_part_soups = soup.find_all("div", attrs={"class": "card-accordion"})

            for part in address_part_soups:
                if "Contact Us" in part.text.strip():
                    address_part_soup = part
                    address_part = str(part)

            result = re.search(r"\d(.*)<br/>", address_part)

            maybe_address = result.group(0)

            address_pieces = maybe_address.split("<br/>")
            if len(address_pieces) > 2:

                address_pieces.pop(-1)

                zipp_check = address_pieces[-1].split(" ")[-1]
                m = re.search(r"\d+$", zipp_check)
                if m is None:
                    address = ""
                    for piece in address_pieces:
                        address = address + piece + " "
                    address = address[:-1]

                    zipp = re.search(r"\d\d\d\d\d", address_part).group(0)

                else:
                    address_pieces.pop(-1)

                    address = ""
                    for piece in address_pieces:
                        address = address + piece + " "
                    address = address[:-1]

                    zipp = zipp_check

                p_tags = address_part_soup.find_all("p")
                for tag in p_tags:
                    if "Phone" in tag.text.strip():
                        phone_text = tag.text.strip().split("Phone")[1]
                        y = 0
                        phone = ""
                        for character in phone_text:
                            m = re.search(r"\d", character)
                            if m is not None:
                                phone = phone + character
                                y = y + 1

                            if y == 10:
                                break

                        break
            else:

                p_tags = address_part_soup.find_all("p")

                address = ""
                for tag in p_tags:
                    if "Phone" in tag.text.strip():
                        zipp = tag.text.strip().split("Phone")[0].split(" ")[-1]

                        phone_text = tag.text.strip().split("Phone")[1]
                        y = 0
                        phone = ""
                        for character in phone_text:
                            m = re.search(r"\d", character)
                            if m is not None:
                                phone = phone + character
                                y = y + 1

                            if y == 10:
                                break

                        break
                    else:
                        address = address + tag.text.strip() + " "
                address = address[:-1]

        if address == "1103 Kingshighway":
            address = "<MISSING>"
            zipp = "<MISSING>"

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
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        hours_of_operations.append(hours)

    df = pd.DataFrame(
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
            "location_type": location_types,
        }
    )

    return df


df = getdata()

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

df.to_csv("data.csv", index=False)
