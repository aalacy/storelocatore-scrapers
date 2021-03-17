import csv
from sgselenium import SgChrome
import time
import bs4


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
    # Your scraper here
    locator_domain = "https://icuracao.com/"
    missingString = "<MISSING>"

    extractable_html = []

    with SgChrome(
        is_headless=True,
    ) as driver:
        driver.get("https://icuracao.com/store-locator")
        time.sleep(20)
        for e in driver.find_elements_by_class_name("aw-storelocator-description"):
            extractable_html.append(e.get_attribute("innerHTML"))

    result = []

    for html in extractable_html:
        s = bs4.BeautifulSoup(html, features="lxml")
        if not s.find("div", {"class": "aw-storelocator-navigation-item-title"}):
            pass
        else:
            name = s.find(
                "div", {"class": "aw-storelocator-navigation-item-title"}
            ).text
            street = s.find("span", {"data-bind": "text: item.street"}).text
            city = s.find("span", {"data-bind": "text: item.city"}).text
            country = s.find("div", {"data-bind": "text: item.country"}).text
            state = s.find("div", {"data-bind": "text: item.region"}).text
            zp = s.find("div", {"data-bind": "text: item.zip"}).text
            m = s.find("div", {"data-bind": "text: item.phone"}).text.split("Open")
            phone = m[0]
            timeArr = []
            for mm in m:
                if phone in mm:
                    pass
                else:
                    parsed = (
                        mm.replace(",", "")
                        .replace(
                            "✔ In-Store Shopping ✔ Curbside Pickup ✔ Delivery Available",
                            "",
                        )
                        .replace("✔", "")
                        .replace("–", "-")
                    )
                    timeArr.append(parsed.strip())
            hours = ", ".join(timeArr)
            result.append(
                [
                    locator_domain,
                    missingString,
                    name,
                    street,
                    city,
                    state,
                    zp,
                    country,
                    missingString,
                    phone,
                    missingString,
                    missingString,
                    missingString,
                    hours,
                ]
            )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
