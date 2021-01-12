import csv
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    base_url = "https://www.mitsubishicars.com/"
    addressess = []
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=100,
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
    for index, zip_code in enumerate(search):
        try:
            link = (
                "https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode="
                + str(zip_code)
                + "&idealer=false&ecommerce=false"
            )
            json_data = session.get(link, headers=headers).json()
        except:
            pass
        for loc in json_data:
            address = loc["address1"].strip()
            if loc["address2"]:
                address += " " + loc["address2"].strip()
            name = loc["dealerName"].strip()
            city = loc["city"].strip().capitalize()
            state = loc["state"].strip()
            zipp = loc["zipcode"]
            phone = loc["phone"].strip()
            country = loc["country"].replace("United States", "US").strip()
            lat = loc["latitude"]
            lng = loc["longitude"]
            link = loc["dealerUrl"]
            storeno = loc["bizId"]
            page_url = ""
            if link:
                page_url = "http://" + link.lower()
                if (
                    "http://www.verneidemitsubishi.com" in page_url
                    or "http://www.kingautomitsubishi.com" in page_url
                    or "http://www.verhagemitsubishi.com" in page_url
                    or "http://www.sisbarro-mitsubishi.com" in page_url
                    or "http://www.delraymitsu.net" in page_url
                ):
                    hours_of_operation = "<INACCESSIBLE>"
                else:
                    try:
                        r1 = session.get(page_url, headers=headers)
                    except:
                        pass
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    if soup1.find("div", {"class": "sales-hours"}):
                        hours_of_operation = " ".join(
                            list(
                                soup1.find(
                                    "div", {"class": "sales-hours"}
                                ).stripped_strings
                            )
                        )
                    elif soup1.find(
                        "ul", {"class": "list-unstyled line-height-condensed"}
                    ):
                        hours_of_operation = " ".join(
                            list(
                                soup1.find(
                                    "ul",
                                    {"class": "list-unstyled line-height-condensed"},
                                ).stripped_strings
                            )
                        )
                    elif soup1.find("div", {"class": "well border-x"}):
                        hours_of_operation = " ".join(
                            list(
                                soup1.find("div", {"class": "well border-x"})
                                .find("table")
                                .stripped_strings
                            )
                        )
                    elif soup1.find("div", {"class": "hours-block pad-2x"}):
                        hours_of_operation = " ".join(
                            list(
                                soup1.find(
                                    "div", {"class": "hours-block pad-2x"}
                                ).stripped_strings
                            )
                        )
                    elif soup1.find("div", {"class": "hoursBox"}):
                        hours_of_operation = " ".join(
                            list(
                                soup1.find(
                                    "div", {"class": "hoursBox"}
                                ).stripped_strings
                            )
                        )
                    else:
                        hours_of_operation = "<INACCESSIBLE>"
            else:
                hours_of_operation = "<MISSING>"
                page_url = ""

            if city == "Little rock" or city == "Charlottesville":
                page_url = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country)
            store.append(storeno)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            try:
                store.append(hours_of_operation.split("} Sales Hours ")[1])
            except:
                store.append(hours_of_operation)
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [
                str(x)
                .encode("ascii", "replace")
                .decode("ascii")
                .strip()
                .replace("?", "")
                if x
                else "<MISSING>"
                for x in store
            ]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
