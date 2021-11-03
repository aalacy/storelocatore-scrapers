import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    base_link = "https://www.mazda.co.uk/api/dealers/address?query=CB4%201SR&limit=150"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    stores = session.get(base_link, headers=headers).json()["data"]["dealers"]

    data = []

    locator_domain = "mazda.co.uk"

    for store in stores:
        location_name = store["name"]
        try:
            street_address = (
                store["address"]["street"] + " " + store["address"]["street2"]
            )
        except:
            street_address = store["address"]["street"]
        city = store["address"]["city"]
        try:
            state = store["address"]["region"]
        except:
            state = "<MISSING>"
        zip_code = store["address"]["zip"]
        country_code = store["address"]["country"]
        store_number = store["dealerNumber"]

        location_type = ""
        types = store["services"]
        for t in types:
            location_type = location_type + ", " + t["name"]

        location_type = location_type[1:].strip()

        latitude = store["address"]["coordinates"]["latitude"]
        longitude = store["address"]["coordinates"]["longitude"]

        try:
            link = store["contact"]["website"]
        except:
            link = store["services"][0]["contact"]["website"]

        if "www" in link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                phone = base.find("span", attrs={"itemprop": "telephone"}).text.strip()
            except:
                phone = store["contact"]["phoneNumber"]["national"]

            try:
                hr_link = (link + base.find(class_="contact-us").a["href"]).replace(
                    "uk//", "uk/"
                )
                req = session.get(hr_link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                hours_of_operation = " ".join(
                    list(base.find_all(class_="loc-hours-table")[0].stripped_strings)
                )
            except:
                try:
                    hours_of_operation = ""
                    hours = store["services"][0]["openingTimes"]
                    for h in hours:
                        hours_of_operation = (
                            hours_of_operation + " " + h["day"] + " " + h["openTime"]
                        ).strip()
                except:
                    hours_of_operation = "<MISSING>"
        else:
            link = "<MISSING>"
            phone = store["contact"]["phoneNumber"]["national"]

            hours_of_operation = ""
            raw_hours = store["services"][0]["openingTimes"]
            for raw_hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + raw_hour["dayOfWeek"]
                    + " "
                    + raw_hour["from"]
                    + "-"
                    + raw_hour["to"]
                ).strip()

            if "SUNDAY" not in hours_of_operation.upper():
                hours_of_operation = hours_of_operation + " SUNDAY CLOSED"

        data.append(
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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
