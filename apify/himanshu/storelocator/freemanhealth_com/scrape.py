import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time
import random

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
                "location_number",
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


def url_list():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    url_list = []
    loc_url = "https://freemanhealth.com/all-locations"
    while True:
        try:
            res = session.get(loc_url, headers=headers)
            soup = BeautifulSoup(res.text, "html5lib")
            curr_url = soup.find(class_="pager__item is-active").find("a").get("href")
            url_list.append(curr_url)
            next_url = (
                soup.find(class_="pager__item pager__item--next").find("a").get("href")
            )
            loc_url = loc_url + next_url
        except AttributeError:
            break
    return url_list


def location_type():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    filter_url = ""
    filter_name = ""
    location_type_dict = {}
    base_url = "https://freemanhealth.com/all-locations"
    res = session.get(base_url, headers=headers)
    soup = BeautifulSoup(res.text, "html5lib")
    filters = soup.find_all(class_="facet-item")
    for filter in filters:
        location_list = []
        filter_name = filter.find(class_="facet-item__value").text
        anchor = filter.find("a")
        url = anchor.get("href")
        if "specialty" in url:
            filter_url = url
            filter_res = session.get("https://freemanhealth.com" + filter_url)
            filter_soup = BeautifulSoup(filter_res.text, "html5lib")
            records = filter_soup.find_all("article", {"role": "article"})
            for record in records:
                location_name = record.find(
                    "h2",
                    {"class": "coh-heading coh-style-heading-3-size coh-ce-4da6d1f4"},
                ).text.strip()
                location_list.append(location_name)
            location_type_dict.update({filter_name: location_list})
    return location_type_dict


def fetch_data(list1, loc_dict):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    locator_domain = "https://freemanhealth.com"
    base_url = "https://freemanhealth.com/all-locations"
    for url in list1:
        base_gap = random.randint(1, 5)
        time.sleep(base_gap)
        page = base_url + url
        res = session.get(page, headers=headers)
        soup = BeautifulSoup(res.text, "html5lib")
        records = soup.find_all("article", {"role": "article"})
        for record in records:
            location_name = record.find(
                "h2", {"class": "coh-heading coh-style-heading-3-size coh-ce-4da6d1f4"}
            ).text.strip()
            street_address = record.find(
                "p", {"class": "coh-paragraph coh-ce-e013c31a"}
            ).text.strip()
            city = record.find(
                "p", {"class": "coh-paragraph coh-ce-6ae15eb3"}
            ).text.split(",")[0]
            state = (
                record.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                .text.split(",")[1]
                .split()[0]
            )
            zip_code = (
                record.find("p", {"class": "coh-paragraph coh-ce-6ae15eb3"})
                .text.split(",")[1]
                .split()[1]
            )
            phone_no = record.find(
                "a", {"class": "coh-link coh-ce-ee7ae836"}
            ).text.strip()
            country_code = "US"
            location_no = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            page_url = "<MISSING>"

            jump_gap = random.randint(1, 3)
            time.sleep(jump_gap)
            jump_url = (
                str(
                    record.find(
                        "a", {"class": "coh-link coh-style-link-with-icon-long"}
                    )
                )
                .split()[3]
                .split('"')[1]
            )
            res2 = session.get(jump_url)
            soup2 = BeautifulSoup(res2.text, "html5lib")
            timing = soup2.find_all("p", {"class": "coh-paragraph"})[-2].text
            if "day" in timing:
                hours_of_operation = timing.replace("\n", ",")

            page_url = jump_url

            for filter, locations in loc_dict.items():
                if location_name in locations:
                    location_type = filter
                    break

            location = []
            location.append(locator_domain if locator_domain else "<MISSING>")
            location.append(location_name if location_name else "<MISSING>")
            location.append(street_address if street_address else "<MISSING>")
            location.append(city if city else "<MISSING>")
            location.append(state if state else "<MISSING>")
            location.append(zip_code if zip_code else "<MISSING>")
            location.append(country_code if country_code else "<MISSING>")
            location.append(location_no if location_no else "<MISSING>")
            location.append(phone_no if phone_no else "<MISSING>")
            location.append(location_type if location_type else "<MISSING>")
            location.append(latitude if latitude else "<MISSING>")
            location.append(longitude if longitude else "<MISSING>")
            location.append(hours_of_operation if hours_of_operation else "<MISSING>")
            location.append(page_url if page_url else "<MISSING>")
            yield location


def myscrape():
    list1 = url_list()
    loc_dict = location_type()
    data = fetch_data(list1, loc_dict)
    write_output(data)


myscrape()
