from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from sgrequests import SgRequests


def getdata():
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

    base_url = "https://www.mackenzieriverpizza.com/locations"
    driver = SgChrome(is_headless=True).driver()

    driver.get(base_url)

    html = driver.page_source

    soup = bs(html, "html.parser")

    while True:
        html = driver.page_source
        soup = bs(html, "html.parser")
        try:
            timer = int(soup.find("div", attrs={"id": "timer"}).text)
            timer = timer + timer
        except Exception:
            while True:
                html = driver.page_source
                soup = bs(html, "html.parser")
                state_grids = soup.find_all(
                    "div", attrs={"class": "header-content-container center"}
                )
                if len(state_grids) == 0:
                    pass
                else:
                    break
            break

    x = y = 0
    while True:
        location_grid = soup.find(
            "div", attrs={"class": "et_pb_row et_pb_row_" + str(x)}
        )

        if x < len(state_grids) + 1:
            if x == 7:
                y = y - 1
            state = state_grids[y].text.strip()

        try:
            grids = location_grid.find_all("div", attrs={"class": "et_pb_text_inner"})
        except Exception:
            break

        for grid in grids:

            locator_domain = "www.mackenzieriverpizza.com"
            page_url = grid.find("a")["href"]
            location_name = grid.find("a").text.strip()
            phone = "".join(
                [
                    character
                    for character in grid.find("p")
                    .text.strip()
                    .replace("\n", "")
                    .split("HOURS")[0][::-1]
                    if character.isdigit()
                ][:10][::-1]
            )

            address = (
                str(grid.find("p")).replace("\n", "").split("<br/>")[0].split(">")[-1]
            )
            city = location_name.split("(")[0].strip()
            hours = (
                grid.find("p")
                .text.strip()
                .replace("\n", "")
                .split("HOURS")[1]
                .replace("DIRECTIONSEATDRINK", "")
                .replace("pm", "pm ")
                .replace("pm  ", "pm ")
                .strip()
            )

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(location_name)
            phones.append(phone)
            street_addresses.append(address)
            citys.append(city)
            hours_of_operations.append(hours)
            country_codes.append("US")

            location_types.append("<MISSING>")
            store_numbers.append("<MISSING>")
            states.append(state)
        x = x + 1
        y = y + 1

    x = 0
    for url in page_urls:
        address = street_addresses[x]
        driver.get(url)
        while True:
            html = driver.page_source
            soup = bs(html, "html.parser")
            try:
                timer = int(soup.find("div", attrs={"id": "timer"}).text)
            except Exception:
                while True:
                    try:
                        html = driver.page_source
                        soup = bs(html, "html.parser")
                        iframe = soup.find("iframe", attrs={"loading": "lazy"})
                        zipp_url = iframe["src"]
                        break
                    except Exception:
                        pass
                break

        zipp_response = session.get(zipp_url).text

        zipp_text = (
            zipp_response.split("initEmbed")[1]
            .split("function onApiLoad")[0]
            .replace("\n", "")
        )
        zipp_text = re.search(r" \d\d\d\d\d", zipp_text).group(0).strip()

        zips.append(zipp_text)

        longitude = iframe["src"].split("!2d")[1].split("!3d")[0]
        latitude = iframe["src"].split("!3d")[1].split("!2m")[0]

        x = x + 1

        latitudes.append(latitude)
        longitudes.append(longitude)

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


getdata()
