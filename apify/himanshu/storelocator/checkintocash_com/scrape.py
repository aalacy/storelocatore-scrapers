import csv
import time

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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
        # Body
        for row in data:
            writer.writerow(row)


def parser(location_soup, url):
    street_address = " ".join(
        list(
            location_soup.find("span", {"class": "c-address-street-1"}).stripped_strings
        )
    )
    if location_soup.find("span", {"class": "c-address-street-2"}) is not None:
        street_address = (
            street_address
            + " "
            + " ".join(
                list(
                    location_soup.find(
                        "span", {"class": "c-address-street-2"}
                    ).stripped_strings
                )
            )
        )
    try:
        name = " ".join(
            list(location_soup.find("h1", {"id": "location-name"}).stripped_strings)
        )
    except:
        return "Skip"
    city = location_soup.find("span", {"class": "c-address-city"}).text
    if city[-1:] == ",":
        city = city[:-1]
    state = location_soup.find("abbr", {"class": "c-address-state"}).text
    store_zip = location_soup.find("span", {"class": "c-address-postal-code"}).text
    if location_soup.find("span", {"itemprop": "telephone"}) is None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("span", {"itemprop": "telephone"}).text
    hours = " ".join(
        list(
            location_soup.find(
                "table", {"class": "c-location-hours-details"}
            ).stripped_strings
        )
    )
    try:
        hours = hours.split("Week Hours")[1].strip()
    except:
        pass
    lat = location_soup.find("meta", {"itemprop": "latitude"})["content"]
    lng = location_soup.find("meta", {"itemprop": "longitude"})["content"]
    store = []
    store.append("https://checkintocash.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append("US")
    store.append(url.split("-")[-1].replace(".html", ""))
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(url)
    return store


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    r = session.get("https://local.checkintocash.com/index.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for states in soup.find_all("a", {"class": "c-directory-list-content-item-link"}):
        if states["href"].count("/") > 1:
            location_request = request_wrapper(
                "https://local.checkintocash.com/" + states["href"].replace("../", ""),
                "get",
                headers=headers,
            )
            location_soup = BeautifulSoup(location_request.text, "lxml")
            store_data = parser(
                location_soup, "https://local.checkintocash.com/" + states["href"]
            )
            yield store_data
        else:
            state_request = request_wrapper(
                "https://local.checkintocash.com/" + states["href"],
                "get",
                headers=headers,
            )
            state_soup = BeautifulSoup(state_request.text, "lxml")
            for city in state_soup.find_all(
                "a", {"class": "c-directory-list-content-item-link"}
            ):
                if city["href"].count("/") > 1:
                    loc_link = "https://local.checkintocash.com/" + city[
                        "href"
                    ].replace("../", "")
                    location_request = request_wrapper(loc_link, "get", headers=headers)
                    location_soup = BeautifulSoup(location_request.text, "lxml")
                    store_data = parser(
                        location_soup,
                        loc_link,
                    )
                    if store_data == "Skip":
                        continue
                    yield store_data
                else:
                    city_link = "https://local.checkintocash.com/" + city[
                        "href"
                    ].replace("../", "")
                    city_request = request_wrapper(city_link, "get", headers=headers)
                    city_soup = BeautifulSoup(city_request.text, "lxml")
                    for location in city_soup.find_all(class_="c-location-grid-item"):
                        loc_link = "https://local.checkintocash.com/" + location.a[
                            "href"
                        ].replace("../", "")
                        location_request = request_wrapper(
                            loc_link, "get", headers=headers
                        )
                        location_soup = BeautifulSoup(location_request.text, "lxml")
                        store_data = parser(
                            location_soup,
                            "https://local.checkintocash.com/"
                            + location.a["href"].replace("../", ""),
                        )
                        if store_data == "Skip":
                            continue
                        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
