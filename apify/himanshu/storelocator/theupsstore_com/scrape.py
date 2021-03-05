import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("theupsstore_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
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


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36"
    }
    sub_url = "https://locations.theupsstore.com/"
    base_url = "https://www.theupsstore.com/"
    r = session.get("https://locations.theupsstore.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    addresses = []
    locator_domain = base_url
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    temp_locations = soup.find("div", {"class": "Directory-content"}).find_all(
        "li", {"class": "Directory-listItem"}
    )

    for loc in temp_locations:

        locations_url = sub_url + loc.find("a", {"class": "Directory-listLink"})["href"]

        try:
            r1 = session.get(locations_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
        except:
            continue

        all_locations = soup1.find("div", {"class": "Directory-content"}).find_all(
            "li", {"class": "Directory-listItem"}
        )

        for page in all_locations:

            loc_count = int(
                page.find("span", {"class": "Directory-listLinkCount"})
                .text.replace("(", "")
                .replace(")", "")
            )

            if loc_count == 1:
                try:
                    page_url = (
                        sub_url
                        + page.find("a", {"class": "Directory-listLink"})["href"]
                    )
                except:
                    page_url = "<MISSING>"

                r2 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = soup2.find("div", {"class": "NAP NAP--location"})

                try:
                    location_name = soup2.find(
                        "span", {"class": "LocationName-geo"}
                    ).text.strip()
                except:
                    location_name = "<MISSING>"
                try:
                    try:
                        street_address = (
                            data.find(
                                "span", {"class": "c-address-street-1"}
                            ).text.strip()
                            + data.find(
                                "span", {"class": "c-address-street-2"}
                            ).text.strip()
                        )
                    except:
                        street_address = data.find(
                            "span", {"class": "c-address-street-1"}
                        ).text.strip()
                except:
                    street_address = "<MISSING>"
                try:
                    city = data.find("span", {"class": "c-address-city"}).text.strip()
                except:
                    city = "<MISSING>"
                try:
                    state = data.find("abbr", {"class": "c-address-state"}).text.strip()
                except:
                    state = "<MISSING>"
                try:
                    zipp = data.find(
                        "span", {"class": "c-address-postal-code"}
                    ).text.strip()
                except:
                    zipp = "<MISSING>"
                country_code = "US"
                try:
                    store_number = soup2.find("h2", {"class": "Heading--3"}).text.split(
                        "#"
                    )[-1]
                except:
                    store_number = "<MISSING>"
                try:
                    phone = data.find(
                        "span",
                        {"class": "c-phone-number-span c-phone-main-number-span"},
                    ).text.strip()
                except:
                    phone = "<MISSING>"
                try:
                    hours_of_operation = (
                        soup2.find("table", {"class": "c-hours-details"})
                        .text.replace("Store HoursDay of the WeekHours", "")
                        .strip()
                    )
                except:
                    hours_of_operation = "<MISSING>"

                if (
                    "https://locations.theupsstore.com/de/delmar/38660-sussex-hwy"
                    in page_url
                ):
                    location_name = "Delmar"
                    street_address = "38660 Sussex Hwy 10"
                    city = "Delmar"
                    state = "DE"
                    zipp = "19940"
                    country_code = "US"
                    store_number = "6948"
                    phone = "(302) 907-0455"

                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store

            else:
                locations_url1 = (
                    sub_url + page.find("a", {"class": "Directory-listLink"})["href"]
                )

                r3 = session.get(locations_url1, headers=headers)
                soup3 = BeautifulSoup(r3.text, "lxml")
                all_locations1 = soup3.find(
                    "div", {"class": "Directory-content"}
                ).find_all("li", {"class": "Directory-listTeaser"})

                for page1 in all_locations1:
                    try:
                        page_url = (
                            sub_url
                            + page1.find(
                                "a", {"class": "Teaser-titleLink js-slide-title"}
                            )["href"]
                        )
                    except:
                        page_url = "<MISSING>"

                    r4 = session.get(page_url, headers=headers)
                    soup4 = BeautifulSoup(r4.text, "lxml")
                    data1 = soup4.find("div", {"class": "NAP NAP--location"})

                    try:
                        location_name = soup4.find(
                            "span", {"class": "LocationName-geo"}
                        ).text.strip()
                    except:
                        location_name = "<MISSING>"
                    try:
                        try:
                            street_address = (
                                data1.find(
                                    "span", {"class": "c-address-street-1"}
                                ).text.strip()
                                + data1.find(
                                    "span", {"class": "c-address-street-2"}
                                ).text.strip()
                            )
                        except:
                            street_address = data1.find(
                                "span", {"class": "c-address-street-1"}
                            ).text.strip()
                    except:
                        street_address = "<MISSING>"
                    try:
                        city = data1.find(
                            "span", {"class": "c-address-city"}
                        ).text.strip()
                    except:
                        city = "<MISSING>"
                    try:
                        state = data1.find(
                            "abbr", {"class": "c-address-state"}
                        ).text.strip()
                    except:
                        state = "<MISSING>"
                    try:
                        zipp = data1.find(
                            "span", {"class": "c-address-postal-code"}
                        ).text.strip()
                    except:
                        zipp = "<MISSING>"
                    country_code = "US"
                    try:
                        store_number = soup4.find(
                            "h2", {"class": "Heading--3"}
                        ).text.split("#")[-1]
                    except:
                        store_number = "<MISSING>"
                    try:
                        phone = data1.find(
                            "span",
                            {"class": "c-phone-number-span c-phone-main-number-span"},
                        ).text.strip()
                    except:
                        phone = "<MISSING>"
                    try:
                        hours_of_operation = (
                            soup4.find("table", {"class": "c-hours-details"})
                            .text.replace("Store HoursDay of the WeekHours", "")
                            .strip()
                        )
                    except:
                        hours_of_operation = "<MISSING>"

                    store = []
                    store.append(base_url)
                    store.append(location_name if location_name else "<MISSING>")
                    store.append(street_address if street_address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append(country_code if country_code else "<MISSING>")
                    store.append(store_number if store_number else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type if location_type else "<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(
                        hours_of_operation if hours_of_operation else "<MISSING>"
                    )
                    store.append(page_url if page_url else "<MISSING>")
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store

    link = "https://locations.theupsstore.com/dc/washington"
    r5 = session.get(link, headers=headers)
    soup5 = BeautifulSoup(r5.text, "lxml")
    all_locations2 = soup5.find("div", {"class": "Directory-content"}).find_all(
        "li", {"class": "Directory-listTeaser"}
    )
    for page2 in all_locations2:
        try:
            page_url = (
                sub_url
                + page2.find("a", {"class": "Teaser-titleLink js-slide-title"})["href"]
            )
        except:
            page_url = "<MISSING>"
        r6 = session.get(page_url, headers=headers)
        soup6 = BeautifulSoup(r6.text, "lxml")
        data2 = soup6.find("div", {"class": "NAP NAP--location"})

        try:
            location_name = soup5.find(
                "span", {"class": "LocationName-geo"}
            ).text.strip()
        except:
            location_name = "<MISSING>"
        try:
            try:
                street_address = (
                    data2.find("span", {"class": "c-address-street-1"}).text.strip()
                    + data2.find("span", {"class": "c-address-street-2"}).text.strip()
                )
            except:
                street_address = data2.find(
                    "span", {"class": "c-address-street-1"}
                ).text.strip()
        except:
            street_address = "<MISSING>"
        try:
            city = data2.find("span", {"class": "c-address-city"}).text.strip()
        except:
            city = "<MISSING>"
        try:
            state = data2.find("abbr", {"class": "c-address-state"}).text.strip()
        except:
            state = "<MISSING>"
        try:
            zipp = data2.find("span", {"class": "c-address-postal-code"}).text.strip()
        except:
            zipp = "<MISSING>"
        country_code = "US"
        try:
            store_number = soup6.find("h2", {"class": "Heading--3"}).text.split("#")[-1]
        except:
            store_number = "<MISSING>"
        try:
            phone = data2.find(
                "span", {"class": "c-phone-number-span c-phone-main-number-span"}
            ).text.strip()
        except:
            phone = "<MISSING>"
        try:
            hours_of_operation = (
                soup6.find("table", {"class": "c-hours-details"})
                .text.replace("Store HoursDay of the WeekHours", "")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
