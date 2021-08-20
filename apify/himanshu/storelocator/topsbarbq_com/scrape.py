import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("topsbarbq_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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


def fetch_data():
    return_main_object = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://topsbarbq.com/"
    locator_domain = "http://topsbarbq.com/locations/"
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
    hours_of_operation = "<MISSING>"
    page_url = locator_domain
    r = session.get("http://topsbarbq.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for loc_col in soup.find_all("div", {"class": "loc-col"}):
        if loc_col.h3 is not None:
            location_name = loc_col.h3.text.strip()
            address = loc_col.find("p", class_="elementor-heading-title")
            latitude = address.find("a")["href"].split("@")[-1].split(",")[0].strip()
            longitude = address.find("a")["href"].split("@")[-1].split(",")[1].strip()
            list_address = list(address.stripped_strings)
            street_address = list_address[0].strip()
            city = list_address[-1].split(",")[0].replace("38107", "").strip()
            state = list_address[-1].split(",")[-1].split()[0].strip()
            if "Memphis" in state:
                state = "TN"
            zipp = list_address[-1].split(",")[-1].split()[-1].strip()
            hours_of_operation = "<MISSING>"
            hours = loc_col.find_all("div", {"class": "loc-hours"})
            for hour in hours:
                if "Store Hours:" in hour.text:
                    hours_of_operation = hour.text.replace("Store Hours:", "").strip()
                    break

            if hours_of_operation == "<MISSING>":
                for hour in hours:
                    if "Temporary Hours:" in hour.text:
                        hours_of_operation = hour.text.replace(
                            "Temporary Hours:", ""
                        ).strip()
                        break

            try:
                hours_of_operation = hours_of_operation.split("Drive")[0].strip()
            except:
                pass
            phone = loc_col.find_all("div", class_="elementor-widget-container")[-1]
            if phone.find("a") is not None:
                phone = phone.find("a").text.strip()
            else:
                phone = "<MISSING>"

            store = []
            store.append(base_url if base_url else "<MISSING>")
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
                hours_of_operation.replace("- Carry Out", "").strip()
                if hours_of_operation
                else "<MISSING>"
            )
            store.append(page_url if page_url else "<MISSING>")
            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
