import csv
import json
import time

from bs4 import BeautifulSoup

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    base_link = "https://www.zerodegreescompany.com/locations"
    api_link = "https://www.powr.io/wix/map/public.json?pageId=rda7c&compId=comp-k8s2ixwy&viewerCompId=comp-k8s2ixwy&siteRevision=970&viewMode=site&deviceType=desktop&locale=en&tz=America%2FLos_Angeles&width=980&height=635&instance=AKbTEpSJ0KaP-oXrw7mpmQ07bp2Z4-gHl1LDreGuypE.eyJpbnN0YW5jZUlkIjoiZGE2MmZiOTMtZTNhYS00OTE5LWFmYTgtMTNiYzA0MjIyOTRlIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDEtMTRUMDc6MTk6NDAuNjkwWiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI1NDkzMzJjZC1jYzk0LTRjZjktYTgzNi04NGRiZjZlNTgzMDMiLCJzaXRlT3duZXJJZCI6IjUxNzMzNWRhLTY4NTQtNDUzYS1iMjg2LTFmNWUxYjk5YjdkMyJ9&currency=USD&currentCurrency=USD&vsi=ab83b947-b1b8-488b-bae5-f7a44332761e&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22ea0ca66b-200b-4429-a25d-8465467649ad%7C1%22%2C%22BSI%22%3A%22ea0ca66b-200b-4429-a25d-8465467649ad%7C1%22%7D&url=https://www.zerodegreescompany.com/locations"
    driver = SgChrome().chrome()

    driver.get(base_link)
    time.sleep(8)
    driver.get(api_link)
    time.sleep(2)
    base = BeautifulSoup(driver.page_source, "lxml")

    items = json.loads(base.text)["content"]["locations"]
    locator_domain = "zerodegreescompany.com"

    data = []
    found_poi = []

    for item in items:
        location_name = BeautifulSoup(item["name"], "lxml").text
        desc = BeautifulSoup(item["description"], "lxml").text
        if "coming" in desc.lower():
            continue

        raw_address = json.loads(BeautifulSoup(item["components"], "lxml").text)
        for i in raw_address:
            add_type = i["types"][0]
            if add_type == "street_number":
                street_number = i["long_name"]
            elif add_type == "route":
                route = i["short_name"]
            elif add_type == "locality":
                city = i["long_name"]
            elif add_type == "administrative_area_level_1":
                state = i["short_name"]
            if add_type == "postal_code":
                zip_code = i["long_name"]
        street_address = street_number + " " + route
        if street_address in found_poi:
            continue
        found_poi.append(street_address)
        country_code = "US"
        location_name = "Zero Degrees - " + location_name
        store_number = "<MISSING>"
        location_type = desc[14:].replace("|", ",").strip().replace(" , ", ", ")
        phone = desc[:14].strip()

        if "(" not in phone:
            phone = item["number"]
            location_type = (
                desc.replace("|", ",")
                .strip()
                .replace(" , ", ", ")
                .replace("ORDER ONLINE", "")
            )
        latitude = item["lat"]
        longitude = item["lng"]

        hours_of_operation = "<MISSING>"

        data.append(
            [
                locator_domain,
                "<MISSING>",
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
