import csv
from bs4 import BeautifulSoup
import time
from sglogging import SgLogSetup
from sgrequests import SgRequests

logger = SgLogSetup().get_logger("subaru_co_uk")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    adressessess = []
    url = "https://subaru.co.uk/wp-admin/admin-ajax.php"
    payload = "action=get_stores_by_name&name=&categories%5B0%5D=&filter%5B161%5D=161"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "PHPSESSID=cda7afd67028f02f6e7b16f289ceb7a5; _gcl_au=1.1.1529865331.1608884585; _ga=GA1.3.1331527989.1608884586; _gid=GA1.3.80330707.1608884586; reevoo_sp_ses.27e8=*; _fbp=fb.2.1608884589800.1113088602; _hjid=50b3da01-a2ae-4402-8886-d000c0d32fd4; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; tms_VisitorID=kqk9p0cexj; tms_wsip=1; __sreff=1608884579794.1608885119221.4; __reff=/ mozilla/5.0 (windows nt 10.0|subaru.co.uk %2F referral %2F / mozilla/5.0 (windows nt 10.0; _tq_id.TV-18908154-1.8472=acd9ffc7332ed0d3.1608884586.0.1608885120..; _gat_UA-4806291-3=1; reevoo_sp_id.27e8=89a387d4-9e0e-4ee7-8ca3-e33ceb6c17a6.1608884588.1.1608885125.1608884588.c45f5a4a-f570-49cf-8321-afa126693430",
        "Referer": "https://subaru.co.uk/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    base_url = "https://www.subaru.co.uk/"
    try:
        soup = session.post(url, headers=headers, data=payload).json()
    except:
        pass
    try:
        for mp1 in soup:
            location_name = soup[mp1]["na"].replace("#038;", " ")
            street_address = soup[mp1]["st"].replace("#038;", " ")
            city = soup[mp1]["ct"]
            zipp = soup[mp1]["zp"]
            if street_address in adressessess:
                continue
            adressessess.append(street_address)
            country_code = "UK"
            phone = ""
            phone = soup[mp1]["te"]
            latitude = soup[mp1]["lat"]
            longitude = soup[mp1]["lng"]
            hours_of_operation = ""
            state = ""
            page_url = ""
            new_page_url = ""
            hours_of_operation = ""
            if soup[mp1]["we"]:
                page_url = soup[mp1]["we"]
                new_page_url = page_url + "/contact"
                r1 = request_wrapper(new_page_url, "get", headers=headers)
                try:
                    soup1 = BeautifulSoup(r1.text, "lxml")
                except:
                    pass
                try:
                    new_page_url = (
                        soup[mp1]["we"]
                        + soup1.find_all("div", {"class": "contact-location-box"})[
                            0
                        ].find("a")["href"]
                    )
                    page_url = (
                        soup[mp1]["we"]
                        + soup1.find_all("div", {"class": "contact-location-box"})[
                            0
                        ].find("a")["href"]
                    )
                    r2 = request_wrapper(page_url, "get", headers=headers)
                    soup3 = BeautifulSoup(r2.text, "lxml")
                    try:
                        state = (
                            list(
                                soup3.find_all(
                                    "div", {"class": "box flexi-height_child"}
                                )[1].stripped_strings
                            )[-3]
                            .strip()
                            .split(",")[-2]
                        )
                    except:
                        pass
                    try:
                        phone = (
                            soup3.find("p", class_="telephone-box")
                            .text.strip()
                            .replace("Telephone: ", "")
                        )
                    except:
                        pass
                    hours_of_operation = " ".join(
                        list(
                            soup3.find("div", {"class": "opening-times-container"})
                            .find("div", {"class": "row"})
                            .stripped_strings
                        )
                    )
                except:
                    try:
                        state = (
                            list(
                                soup1.find_all(
                                    "div", {"class": "box flexi-height_child"}
                                )[1].stripped_strings
                            )[-3]
                            .strip()
                            .split(",")[-2]
                        )
                    except:
                        pass
                    try:
                        phone = (
                            soup1.find("p", class_="telephone-box")
                            .text.strip()
                            .replace("Telephone: ", "")
                        )
                    except:
                        pass
                    try:
                        hours_of_operation = " ".join(
                            list(
                                soup1.find("div", {"class": "opening-times-container"})
                                .find("div", {"class": "row"})
                                .stripped_strings
                            )
                        )
                    except:
                        pass
            store_number = soup[mp1]["ID"]
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            if "Middletown," in street_address:
                new_page_url = "https://www.simpsons-subaru.co.uk/contact?location=8408"
            if "Cavendish Street," in street_address:
                new_page_url = (
                    "https://www.colinappleyardcars-subaru.co.uk/contact?location=8357"
                )
            if "Lockwood Road" in street_address:
                new_page_url = (
                    "https://www.colinappleyardcars-subaru.co.uk/contact?location=8358"
                )
            store.append(
                street_address.replace(",", " ") if street_address else "<MISSING>"
            )
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(
                hours_of_operation.replace("\n", "").strip()
                if hours_of_operation
                else "<MISSING>"
            )
            store.append(new_page_url if new_page_url else "<MISSING>")
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
    except:
        pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
