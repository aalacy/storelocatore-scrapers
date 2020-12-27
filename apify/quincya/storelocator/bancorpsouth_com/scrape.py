import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    locator_domain = "bancorpsouth.com"

    all_store_data = []
    all_links = []

    base_link = "https://www.bancorpsouth.com/sitemap.xml"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("loc")
    for item in items:
        if "find-a-location/" in item.text:
            link = item.text
            if link not in all_links:
                all_links.append(link)

    for link in all_links:
        if "atm" in link:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        raw_address = list(
            base.find(class_="row-fluid branch-info")
            .find(class_="span6")
            .stripped_strings
        )

        street_address = " ".join(raw_address[:-3]).strip()
        city_line = raw_address[-3].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address[-1].split("or")[0].strip()

        if (
            "temporarily closed"
            in base.find(class_="row-fluid branch-info").text.lower()
        ):
            hours_of_operation = "Temporarily Closed"
        else:
            hours_of_operation = (
                " ".join(
                    list(
                        base.find(class_="row-fluid branch-info")
                        .find_all(class_="span6")[1]
                        .stripped_strings
                    )[1:3]
                )
                .split("Drive")[0]
                .split("Services")[0]
                .replace("  ", " ")
                .strip()
            )
        if not hours_of_operation:
            try:
                hours_of_operation = (
                    list(
                        base.find(class_="row-fluid branch-info")
                        .find_all(class_="span6")[1]
                        .stripped_strings
                    )[0]
                    .replace("Lobby:", "")
                    .strip()
                )
            except:
                hours_of_operation = "<MISSING>"

        try:
            map_str = base.find(id="content").text
            re.findall(r"[0-9]{2}\.[0-9]+", map_str)[0]
            latitude = re.findall(r"[0-9]{2}\.[0-9]+", map_str)[0]
            longitude = re.findall(r"-[0-9]{2,3}\.[0-9]+", map_str)[0]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        all_store_data.append(
            [
                locator_domain,
                link,
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

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
