import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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


def fetch_data():
    addresses = []
    base_url = "https://freemanhealth.com"
    url = "https://freemanhealth.com/all-locations"

    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    loc_types = soup.find_all("li", {"class": "facet-item"})[:-3]

    for locs in loc_types:

        location_type = locs.find("span", {"class": "facet-item__value"}).text

        counts = (
            locs.find("span", {"class": "facet-item__count"})
            .text.replace("(", "")
            .replace(")", "")
        )

        link = locs.find("a").get("href")

        page_url = base_url + link

        r2 = session.get(page_url)
        soup2 = BeautifulSoup(r2.text, "lxml")
        medicals = soup2.find_all("article", {"role": "article"})

        for med in medicals:
            loc_name = med.find(
                "h2", {"class": "coh-heading coh-style-heading-3-size coh-ce-4da6d1f4"}
            ).text
            street1 = med.find_all("p", {"class": "coh-paragraph coh-ce-e013c31a"})[
                0
            ].text
            street2 = med.find_all("p", {"class": "coh-paragraph coh-ce-e013c31a"})[1]
            if street2:
                street1 = street1 + " " + street2.text
            city = med.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"}).text.split(
                ","
            )[0]
            state = (
                med.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                .text.split(",")[1]
                .split()[0]
            )
            zip_code = (
                med.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                .text.split(",")[1]
                .split()[-1]
            )
            if len(zip_code) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = "<MISSING>"
            try:
                phone = (
                    med.find("a", {"class": "coh-link coh-ce-ee7ae836"})
                    .text.strip()
                    .replace(".", "-")
                )
            except:
                phone = "<MISSING>"

            med_url = med.find(
                "a", {"class": "coh-link coh-style-link-with-icon-long"}
            ).get("href")

            soup3 = BeautifulSoup(session.get(med_url).text, "lxml")

            hours = ""
            try:
                hours = list(
                    soup3.find(
                        "h5", text=" Hours of Operation "
                    ).next_element.next_element.next_element.stripped_strings
                )
            except:
                try:
                    hours = list(
                        soup3.find(
                            "h5", text=" Hours "
                        ).next_element.next_element.next_element.stripped_strings
                    )
                except:
                    try:
                        hours = list(
                            soup3.find(
                                "h2", text="Hours"
                            ).next_element.next_element.next_element.stripped_strings
                        )
                    except:
                        hours = "<MISSING>"
            hours_of_operation = "".join(hours)
            if street1 == "2531 East 32nd Street":
                loc_name = loc_name.replace("﻿", "")
            store = []
            store.append(base_url)
            store.append(loc_name)
            store.append(street1)
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip_code if zip_code else "<MISSING>")
            store.append(country_code)
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append(med_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store

        if int(counts) > 10:
            while True:
                try:
                    next_page = soup2.find("a", {"rel": "next"}).get("href")
                    next_page_url = url + next_page
                    r3 = session.get(next_page_url)
                    soup4 = BeautifulSoup(r3.text, "lxml")
                    medicals = soup4.find_all("article", {"role": "article"})
                    soup2 = soup4
                except:
                    break
                for med in medicals:
                    loc_name = med.find(
                        "h2",
                        {
                            "class": "coh-heading coh-style-heading-3-size coh-ce-4da6d1f4"
                        },
                    ).text
                    street1 = med.find_all(
                        "p", {"class": "coh-paragraph coh-ce-e013c31a"}
                    )[0].text
                    street2 = med.find_all(
                        "p", {"class": "coh-paragraph coh-ce-e013c31a"}
                    )[1]
                    if street2:
                        street1 = street1 + " " + street2.text
                    city = med.find(
                        "p", {"class": "coh-paragraph coh-ce-6ae15eb3"}
                    ).text.split(",")[0]
                    state = (
                        med.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                        .text.split(",")[1]
                        .split()[0]
                    )
                    zip_code = (
                        med.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                        .text.split(",")[1]
                        .split()[-1]
                    )
                    if len(zip_code.strip()) == 5:
                        country_code = "US"
                    else:
                        country_code = "CA"
                    store_number = "<MISSING>"
                    try:
                        phone = (
                            med.find("a", {"class": "coh-link coh-ce-ee7ae836"})
                            .text.strip()
                            .replace(".", "-")
                        )
                    except:
                        phone = "<MISSING>"

                    med_url = med.find(
                        "a", {"class": "coh-link coh-style-link-with-icon-long"}
                    ).get("href")

                    soup5 = BeautifulSoup(session.get(med_url).text, "lxml")
                    hours = ""
                    try:
                        hours = list(
                            soup5.find(
                                "h5", text=" Hours of Operation "
                            ).next_element.next_element.next_element.stripped_strings
                        )
                    except:
                        try:
                            hours = list(
                                soup5.find(
                                    "h5", text=" Hours "
                                ).next_element.next_element.next_element.stripped_strings
                            )
                        except:
                            try:
                                hours = list(
                                    soup5.find(
                                        "h2", text="Hours"
                                    ).next_element.next_element.next_element.stripped_strings
                                )
                            except:
                                hours = "<MISSING>"

                    hours_of_operation = "".join(hours)
                    store = []
                    store.append(base_url)
                    store.append(loc_name)
                    store.append(street1)
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zip_code if zip_code else "<MISSING>")
                    store.append(country_code)
                    store.append(store_number)
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type)
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(hours_of_operation)
                    store.append(med_url)
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
