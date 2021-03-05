import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("abbeycarpet_com")
session = SgRequests()


def write_output(data):
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


def fetch_data():

    adress = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.abbeycarpet.com"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=200,
        max_radius_miles=100,
    )
    for zip_code in search:
        location_url = (
            "https://www.abbeycarpet.com/StoreLocator.aspx?searchZipCode="
            + str(zip_code)
        )
        try:
            r = session.get(location_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
        except:
            continue

        links = soup.find_all("a", {"class": "search-store__results-links-site"})
        for link in links:
            page_url = base_url + link.get("href")
            home = session.get(page_url)
            page_soup = BeautifulSoup(home.text, "lxml")
            store_number = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            location_type = "<MISSING>"

            try:
                address = page_soup.find("a", {"class": "footer-address"})[
                    "href"
                ].split("/")[-1]
                if len(address.split(",")) == 4:
                    name = address.split(",")[0]
                    street = address.split(",")[1]
                else:
                    name = address.split(",")[0]
                    street = "".join(address.split(",")[1:-2])
                city = address.split(",")[-2]
                state = address.split(",")[-1].split()[:-1]
                if len(address.split(",")[-1].split()) > 2:
                    state = " ".join(state)
                else:
                    state = address.split(",")[-1].split()[0]
                zip_code = address.split(",")[-1].split()[-1]
                phone = page_soup.find("a", {"class": "footer-phone"}).text
                location_type = "<MISSING>"
                hrs = page_soup.find("p", {"class": "hours"}).text.split("\n")
                hours_of_operation = " ".join(hrs)
            except:
                try:
                    divs = page_soup.find_all(
                        "div", {"class": "col-xs-12 col-sm-12 col-md-3 col-lg-3 "}
                    )
                    for div in divs:
                        lst = div.text.split("\n")
                        del lst[0]
                        del lst[-1]
                        if len(lst) > 4:
                            del lst[1]
                            name = lst[0]
                            street = lst[1]
                            city = lst[2].split(",")[0]
                            state = lst[2].split(",")[1].split()[0]
                            zip_code = lst[2].split(",")[1].split()[-1]
                            for i in lst:
                                if "T:" in i:
                                    phone = i[3:]

                        else:
                            hours_of_operation = " ".join(lst[1:])

                except:
                    continue

            if page_soup.find("div", {"class": "mapWrapper"}) is not None:
                iframe = page_soup.find("div", {"class": "mapWrapper"}).find("iframe")
                src = iframe["src"]
                if src is not None and src != []:
                    if "!3d" in src:
                        longitude = src.split("!2d")[1].split("!3d")[0]
                        latitude = src.split("!2d")[1].split("!3d")[1].split("!")[0]
                    elif "place?zoom" in src:
                        latitude = src.split("=")[2].split(",")[0]
                        longitude = src.split("=")[2].split(",")[1].split("&")[0]
                    elif "!3f" in src:
                        longitude = src.split("!2d")[1].split("!3f")[0]
                        latitude = src.split("!2d")[1].split("!3f")[1].split("!4f")[0]
                    else:
                        latitude = ""
                        longitude = ""
                else:
                    latitude = ""
                    longitude = ""
            else:
                try:
                    src = page_soup.find_all("iframe")[-1]
                    if "!3d" in src["src"]:
                        longitude = src["src"].split("!2d")[1].split("!3d")[0]
                        latitude = (
                            src["src"].split("!2d")[1].split("!3d")[1].split("!")[0]
                        )
                    elif "place?zoom" in src:
                        latitude = src["src"].split("=")[2].split(",")[0]
                        longitude = src["src"].split("=")[2].split(",")[1].split("&")[0]
                    elif "!3f" in src["src"]:
                        longitude = src["src"].split("!2d")[1].split("!3f")[0]
                        latitude = (
                            src["src"].split("!2d")[1].split("!3f")[1].split("!4f")[0]
                        )
                    else:
                        latitude = ""
                        longitude = ""
                except:
                    latitude = ""
                    longitude = ""

            if name == "font>":
                name = "Southern Carpet & Interiors"
            store = []
            store.append(base_url)
            store.append(name)
            store.append(street)
            store.append(city)
            store.append(state)
            store.append(zip_code)
            if zip_code.isdigit():
                store.append("US")
            else:
                store.append("CA")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(str(latitude) if latitude else "<MISSING>")
            store.append(str(longitude) if longitude else "<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in adress:
                continue
            adress.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
