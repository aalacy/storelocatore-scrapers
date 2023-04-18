import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.rushtruckcenters.com"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "ASP.NET_SessionId=2ed05bksxqgburu2r3tmluvk; SC_ANALYTICS_GLOBAL_COOKIE=b7a00fa49d4148b3b34d1c9fdfe2e14b; SC_ANALYTICS_SESSION_COOKIE=4880118212F4409CB9B0116283B95A60|0|2ed05bksxqgburu2r3tmluvk; _ga=GA1.2.389575146.1610018644; _gid=GA1.2.251603942.1610018644; _gat_UA-44301006-1=1; _fbp=fb.1.1610018646829.1494000126; _hjTLDTest=1; _hjid=68aa9bbd-faee-4805-90c0-a3721a26bb2a; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=1",
        "Host": "www.rushtruckcenters.com",
        "Referer": "https://www.rushtruckcenters.com/locations/location-search",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    res = session.get(
        "https://www.rushtruckcenters.com/api/TrucksLocationSearch?", headers=headers
    )

    store_list = json.loads(res.text)["TrucksLocationSearchResults"]
    data = []
    for store in store_list:
        page_url = base_url + store["LocationUrl"]
        res = session.get(page_url)
        soup = bs(res.text, "lxml")
        location_name = store["Title"]
        address = soup.select_one("p.location-address").string.split("\xa0\xa0")
        address_detail = address[0].split(", ")
        state = address_detail.pop()
        city = address_detail.pop()
        street_address = ", ".join(address_detail)
        zip = address.pop()
        country_code = "<MISSING>"
        geo = soup.select_one("div.location-map a")["href"].split("q=").pop()
        latitude = geo.split(",")[0]
        longitude = geo.split(",")[1]
        store_number = store["LocationId"]
        location_type = "<MISSING>"
        phone = store["PhoneNumbers"][0]["Value"]

        serviceDOMs = soup.select(".location-departments ul li")
        for serviceDOM in serviceDOMs:
            salesTag = serviceDOM.select("p.bold")
            if len(salesTag) > 0:
                hours_of_operation = serviceDOM.text
                hours_of_operation = hours_of_operation.replace("\n", "")
                break

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
