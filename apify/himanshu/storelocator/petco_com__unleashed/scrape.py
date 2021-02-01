import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("petco_com__unleashed")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://stores.petco.com"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    addressses = []
    state_divs = soup.find_all("div", {"class": "map-list-item-wrap is-single"})
    for i, st_div in enumerate(state_divs, start=1):
        if i == 53:
            break

        st_link = st_div.find("a", {"class": "gaq-link"})["href"]
        req1 = session.get(st_link, headers=headers)
        cities_soup = BeautifulSoup(req1.text, "lxml")
        ct_divs = cities_soup.find_all("div", {"class": "map-list-item-wrap is-single"})
        for city in ct_divs:
            if city.find("a", {"class": "gaq-link"}):
                page_url = city.find("a", {"class": "gaq-link"})["href"]
                req2 = session.get(page_url, headers=headers)
                store_soup = BeautifulSoup(req2.text, "lxml")
                location_name = city.find("a", {"class": "gaq-link"})["title"].split(
                    "|"
                )[::-1]
                location_name = " ".join(location_name)
                store_number = "<MISSING>"
                address = store_soup.find("p", {"class": "address"})
                street = address.find_all("span")[0].text
                cty = address.find_all("span")[1].text.split(",")[0]
                st = address.find_all("span")[1].text.split(",")[1].split()[0]
                zip_code = address.find_all("span")[1].text.split(",")[1].split()[1]
                phone = store_soup.find("a", {"class": "phone gaq-link"}).text.strip()
                lat_lng = store_soup.find("a", {"class": "directions"})["href"].split(
                    "="
                )[-1]
                latitude = lat_lng.split(",")[0]
                longitude = lat_lng.split(",")[1]

                new_link = store_soup.find(
                    "a", {"class": "btn btn-primary full-width store-info gaq-link"}
                )["href"]
                req3 = session.get(new_link)
                last_soup = BeautifulSoup(req3.text, "lxml")

                try:
                    hrs_rows = last_soup.find_all("div", {"class": "day-hour-row"})
                    openingHours = ""
                    for row in hrs_rows:
                        day = row.find("span", {"class": "daypart"}).text.strip()
                        opening = row.find("span", {"class": "time-open"}).text.strip()
                        closing = row.find("span", {"class": "time-close"}).text.strip()
                        openingHours = (
                            openingHours + day + " " + opening + "-" + closing + " "
                        )
                except:
                    openingHours = "<MISSING>"

                location_type = "PetStore"

                store = []
                store.append(base_url)
                store.append(location_name.strip())
                store.append(street.strip())
                store.append(cty.strip())
                store.append(st.strip())
                store.append(zip_code.strip())
                if zip_code.strip().isdigit():
                    store.append("US")
                else:
                    store.append("CA")
                store.append(store_number.strip())
                store.append(phone.strip())
                store.append(location_type)
                store.append(str(latitude).strip() if latitude else "<MISSING>")
                store.append(str(longitude).strip() if longitude else "<MISSING>")
                store.append(openingHours.strip())
                store.append(new_link.strip())
                if store[2] in addressses:
                    continue
                addressses.append(store[2])
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
