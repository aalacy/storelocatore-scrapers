from bs4 import BeautifulSoup
from sgrequests import SgRequests
import csv

session = SgRequests()
base_url = "https://stores.footaction.com/"


def fetch_data():
    main_url = "https://stores.footaction.com/index.html"
    main_page = session.get(main_url)
    main_soup = BeautifulSoup(main_page.text, "lxml")
    states = main_soup.find_all("li", {"class": "Directory-listItem"})
    for state in states:
        state_url = state.find("a", {"class": "Directory-listLink"}).get("href")
        state_page_url = (base_url + state_url).replace(
            "https://stores.footaction.com/us/nv/las-vegas.html",
            "https://stores.footaction.com/us/nv.html",
        )

        city_counts = (
            state.find("a", {"class": "Directory-listLink"})
            .get("data-count")
            .replace("(", "")
            .replace(")", "")
        )
        if int(city_counts) > 1:
            states_page = session.get(state_page_url)
            state_soup = BeautifulSoup(states_page.text, "lxml")
            cities = state_soup.find_all("li", {"class": "Directory-listItem"})
            for city in cities:
                city_url = city.find("a", {"class": "Directory-listLink"}).get("href")
                city_page_url = base_url + city_url
                store_counts = (
                    city.find("a", {"class": "Directory-listLink"})
                    .get("data-count")
                    .replace("(", "")
                    .replace(")", "")
                )
                if int(store_counts) > 1:
                    stores_page = session.get(city_page_url)
                    stores_soup = BeautifulSoup(stores_page.text, "lxml")
                    stores = stores_soup.find_all(class_="Directory-listTeaser")
                    for store in stores:
                        store_url = store.find("a").get("href").split("/")[-1]
                        final_page_url = city_page_url.replace(".html", "/") + store_url
                        final_page = session.get(final_page_url)
                        final_soup = BeautifulSoup(final_page.text, "lxml")
                        name = final_soup.find("h1", {"class": "Hero-title"}).get_text()
                        street = final_soup.find(
                            "span", {"class": "c-address-street-1"}
                        ).get_text()
                        cty = final_soup.find(
                            "span", {"class": "c-address-city"}
                        ).get_text()
                        st = final_soup.find("abbr", {"class": "c-address-state"}).get(
                            "title"
                        )
                        pin = final_soup.find(
                            "span", {"class": "c-address-postal-code"}
                        ).get_text()
                        if len(pin) == 5:
                            country_code = "US"
                        else:
                            country_code = "CA"
                        store_number = "<MISSING>"
                        phone = final_soup.find("div", {"id": "phone-main"}).get_text()
                        location_type = "<MISSING>"
                        location = (
                            final_soup.find("meta", {"name": "geo.position"})
                            .get("content")
                            .split(";")
                        )
                        lati = location[0]
                        longi = location[1]
                        hrs_table = final_soup.find("div", {"class": "c-hours"})
                        days = hrs_table.find_all("tr")
                        hours_of_operation = ""
                        for day in days[1:]:
                            hours_of_operation = (
                                hours_of_operation + " " + day.get_text()
                            )
                        page_url = final_page_url

                        locations = []
                        locations.append(base_url)
                        locations.append(name)
                        locations.append(street)
                        locations.append(cty)
                        locations.append(st)
                        locations.append(pin)
                        locations.append(country_code)
                        locations.append(store_number)
                        locations.append(phone)
                        locations.append(location_type)
                        locations.append(lati)
                        locations.append(longi)
                        locations.append(hours_of_operation.replace("day", "day "))
                        locations.append(page_url)
                        yield locations

                else:

                    stores_page = session.get(city_page_url)
                    stores_soup = BeautifulSoup(stores_page.text, "lxml")
                    name = stores_soup.find("h1", {"class": "Hero-title"}).get_text()
                    street = stores_soup.find(
                        "span", {"class": "c-address-street-1"}
                    ).get_text()
                    cty = stores_soup.find(
                        "span", {"class": "c-address-city"}
                    ).get_text()
                    try:
                        st = stores_soup.find("abbr", {"class": "c-address-state"}).get(
                            "title"
                        )
                    except:
                        st = "<MISSING>"
                    pin = stores_soup.find(
                        "span", {"class": "c-address-postal-code"}
                    ).get_text()
                    if len(pin) == 5:
                        country_code = "US"
                    else:
                        country_code = "CA"
                    store_number = "<MISSING>"
                    phone = stores_soup.find("div", {"id": "phone-main"}).get_text()
                    location_type = "<MISSING>"
                    location = (
                        stores_soup.find("meta", {"name": "geo.position"})
                        .get("content")
                        .split(";")
                    )
                    lati = location[0]
                    longi = location[1]
                    hrs_table = stores_soup.find("div", {"class": "c-hours"})
                    days = hrs_table.find_all("tr")
                    hours_of_operation = ""
                    for day in days[1:]:
                        hours_of_operation = hours_of_operation + " " + day.get_text()
                    page_url = city_page_url

                    locations = []
                    locations.append(base_url)
                    locations.append(name)
                    locations.append(street)
                    locations.append(cty)
                    locations.append(st)
                    locations.append(pin)
                    locations.append(country_code)
                    locations.append(store_number)
                    locations.append(phone)
                    locations.append(location_type)
                    locations.append(lati)
                    locations.append(longi)
                    locations.append(hours_of_operation.replace("day", "day "))
                    locations.append(page_url)
                    yield locations

        else:
            stores_page = session.get(state_page_url)
            stores_soup = BeautifulSoup(stores_page.text, "lxml")
            name = stores_soup.find("h1", {"class": "Hero-title"}).get_text()
            street = stores_soup.find(
                "span", {"class": "c-address-street-1"}
            ).get_text()
            cty = stores_soup.find("span", {"class": "c-address-city"}).get_text()
            st = stores_soup.find("abbr", {"class": "c-address-state"}).get("title")
            pin = stores_soup.find(
                "span", {"class": "c-address-postal-code"}
            ).get_text()
            if len(pin) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = "<MISSING>"
            phone = stores_soup.find("div", {"id": "phone-main"}).get_text()
            location_type = "<MISSING>"
            location = (
                stores_soup.find("meta", {"name": "geo.position"})
                .get("content")
                .split(";")
            )
            lati = location[0]
            longi = location[1]
            hrs_table = stores_soup.find("div", {"class": "c-hours"})
            days = hrs_table.find_all("tr")
            hours_of_operation = ""
            for day in days[1:]:
                hours_of_operation = hours_of_operation + " " + day.get_text()
            page_url = state_page_url

            locations = []
            locations.append(base_url)
            locations.append(name)
            locations.append(street)
            locations.append(cty)
            locations.append(st)
            locations.append(pin)
            locations.append(country_code)
            locations.append(store_number)
            locations.append(phone)
            locations.append(location_type)
            locations.append(lati)
            locations.append(longi)
            locations.append(hours_of_operation.replace("day", "day "))
            locations.append(page_url)
            yield locations


def load_data(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def scrape():
    data = fetch_data()
    load_data(data)


if __name__ == "__main__":
    scrape()
