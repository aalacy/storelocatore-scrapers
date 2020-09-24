import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from requests.exceptions import RequestException  # ignore_check


def log(*args, **kwargs):
    if show_logs == True:
        print(" ".join(map(str, args)), **kwargs)
        print("")


def override_retries():
    # monkey patch sgrequests in order to set max retries
    import requests

    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


def get(url, headers, attempts=1):
    global session
    if attempts == 11:
        raise SystemExit(f"Could not get {url} after {attempts-1} attempts.")
    try:
        log(f"getting {url}")
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r
    except (RequestException, Exception) as ex:
        status_code = get_response_status_from_err(ex)
        if status_code == 404:
            log(f"Got 404 for {url}")
            log(
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            )
            return None

        if status_code == 503:
            response_text = get_response_text_from_err(ex)
            if "Down for Maintenance" in response_text:
                log(f"Got 'Down for Maintenance (503 error)' for {url}")
                log(
                    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                )
                return None

        log(f">>> resetting session after exception getting {url} : {ex}")
        session = SgRequests()
        return get(url, headers, attempts + 1)


def get_response_status_from_err(err):
    if (
        hasattr(err, "response")
        and err.response is not None
        and hasattr(err.response, "status_code")
    ):
        return err.response.status_code
    return None


def get_response_text_from_err(err):
    if (
        hasattr(err, "response")
        and err.response is not None
        and hasattr(err.response, "text")
    ):
        return err.response.text
    return None


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


show_logs = False
override_retries()
session = SgRequests()


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    addressess = []
    addresses = []
    base_url = "https://www.educationaloutfitters.com"
    r = get("http://www.educationaloutfitters.com/states", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    # it will used in store data.
    locator_domain = base_url
    location_name = ""
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
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "http://www.educationaloutfitters.com/states"
    for script in soup.find_all("li", {"class": "navList-item"}):
        r1 = get(script.find("a")["href"], headers=headers)
        if not r1:
            continue
        soup1 = BeautifulSoup(r1.text, "lxml")
        for lep in soup1.find_all("article", {"class": "modern__card"}):
            location_name = lep.find("a", {"class": "modern__card-title-link"}).text
            r_location = get(lep.find("a")["href"], headers=headers)
            if not r_location:
                continue
            soup_location = BeautifulSoup(r_location.text, "html.parser")
            page_urls = soup_location.find("div", {"class": "store-button"}).find("a")[
                "href"
            ]
            log(page_urls)
            r4 = get(page_urls, headers=headers)
            if not r4:
                continue
            soup5 = BeautifulSoup(r4.text, "lxml")
            try:
                hours_of_operation = (
                    " ".join(
                        list(
                            soup5.find("p", {"class": "basic__hours"}).stripped_strings
                        )
                    )
                    .replace("Customer Service Hours:", "")
                    .replace("Store Hours:", "")
                )
            except:
                hours_of_operation = "<MISSING>"
            d = soup_location.find("li", {"class": "store-address"})
            full_detail = list(d.stripped_strings)
            phone = soup_location.find("li", {"class": "store-tel"}).text.strip()
            full_address = full_detail[1:]
            location_name = full_detail[0]
            if len(full_address) == 1:
                street_address = "<MISSING>"
                city = full_address[0].split(",")[0]
                state = full_address[0].split(",")[1]
            elif len(full_address) == 2:
                street_address = " ".join(full_address[:-1])
                city = full_address[-1].split(",")[0]
                state = (
                    full_address[-1]
                    .split(",")[-1]
                    .strip()
                    .split()[0]
                    .replace("78213", "TX")
                )
                zipp = full_address[-1].split(",")[-1].strip().split()[-1]
            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state.strip(),
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation.replace("Store Hours for Curb-side Pick-up:", "")
                .replace("REQUIRED APPOINTMENT to shop in store  ", "")
                .strip(),
                page_urls,
            ]
            if str(store[2] + store[-1]) in addressess:
                continue
            addressess.append(str(store[2] + store[-1]))
            log("data = " + str(store))
            log(
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            )
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
