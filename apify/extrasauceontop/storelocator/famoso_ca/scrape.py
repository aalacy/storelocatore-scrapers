from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import re
import pandas as pd


def reset_sessions(data_url):

    s = SgRequests()

    driver = SgChrome().driver()
    driver.get(data_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = data_url + incap_str

    s.get(incap_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            continue


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
url = "https://famoso.ca/locations/"

new_sess = reset_sessions(url)

s = new_sess[0]
headers = new_sess[1]
response_text = new_sess[2]

soup = bs(response_text, "html.parser")
grids = soup.find_all("div", attrs={"class": "prov-holder"})

for grid in grids:
    state = grid.find("h1").text.strip()
    li_tags = grid.find_all("li")
    for li_tag in li_tags:
        locator_domain = "famoso.ca"
        page_url = li_tag["data-location-url"]
        location_name = li_tag.find("a").text.strip().replace("â€“", "")
        address_parts = li_tag.find("p").text.strip().split("\n")
        address_status = "Lost"
        city_status = "Lost"
        for line in address_parts:
            if bool(re.search(r"\d", line)) is True and address_status == "Lost":
                address = line
                address_status = "Found"

            elif address_status == "Found" and "," in line and city_status == "Lost":
                zipp_index = address_parts.index(line) + 1
                city = line.split(", ")[0]
                state = line.split(", ")[1]
                city_status = "Found"

                zipp = (
                    address_parts[zipp_index].split(" ")[0]
                    + " "
                    + address_parts[zipp_index].split(" ")[1].replace(",", "")
                )
                country_code = "CA"
        store_number = li_tag["data-post-id"]
        phone = li_tag.find("div", attrs={"class": "loc-phone sans-serif"}).text.strip()
        location_type = "<MISSING>"
        latitude = li_tag["data-post-lat"]
        longitude = li_tag["data-post-lng"]

        hours_data = s.get(page_url, headers=headers).text

        hours_soup = bs(hours_data, "html.parser")

        days = hours_soup.find_all("span", attrs={"class": "day-name"})
        start_times = hours_soup.find_all("span", attrs={"class": "time-from"})
        end_times = hours_soup.find_all("span", attrs={"class": "time-to"})

        hours = ""
        for x in range(len(days)):
            day = days[x].text.strip()
            start_time = start_times[x].text.strip()
            end_time = end_times[x].text.strip()

            hours = hours + day + " " + start_time + "-" + end_time + ", "

        hours = hours[:-2]
        if hours == "":
            new_sess = reset_sessions(page_url)
            s = new_sess[0]
            headers = new_sess[1]
            hours_data = new_sess[2]

            hours_soup = bs(hours_data, "html.parser")

            days = hours_soup.find_all("span", attrs={"class": "day-name"})
            start_times = hours_soup.find_all("span", attrs={"class": "time-from"})
            end_times = hours_soup.find_all("span", attrs={"class": "time-to"})

            hours = ""
            for x in range(len(days)):
                day = days[x].text.strip()
                start_time = start_times[x].text.strip()
                end_time = end_times[x].text.strip()

                hours = hours + day + " " + start_time + "-" + end_time + ", "

            hours = hours[:-2]

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
