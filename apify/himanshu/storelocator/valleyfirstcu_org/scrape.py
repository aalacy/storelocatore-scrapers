import csv

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


def fetch_data():
    header = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    return_main_object = []
    base_url = "https://www.valleyfirstcu.org/locations/"
    r = session.get(base_url, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    db = soup.table.find_all("td")

    for idx, val in enumerate(db):

        locator_domain = "https://www.valleyfirstcu.org"

        if len(val.find_all("p")) == 3:
            location_name = val.find_all("p")[0].text.strip()
            street_address = (
                val.find_all("p")[1].text.replace("\xa0", " ").split("\n")[-3].strip()
            )

            city = (
                val.find_all("p")[1].text.split("\n")[-2].strip().split(",")[0].strip()
            )
            state = (
                val.find_all("p")[1]
                .text.split("\n")[-2]
                .strip()
                .split(",")[1]
                .strip()
                .split(" ")[0]
                .strip()
            )
            zip = (
                val.find_all("p")[1]
                .text.split("\n")[-2]
                .strip()
                .split(",")[1]
                .strip()
                .split(" ")[1]
                .strip()
            )

            phone = val.find_all("p")[1].text.split("\n")[-1].strip()
            hours_of_operation = (
                " ".join(
                    val.find_all("p")[-1].text.strip().replace("Hours:", "").split("\n")
                )
                .replace("  ", "")
                .replace("\xa0", " ")
                .strip()
            )
        else:
            raw_data = list(val.stripped_strings)
            if "location" in raw_data[1]:
                raw_data.pop(1)
            location_name = raw_data[0]
            street_address = raw_data[1]
            city_line = raw_data[2].split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip = city_line[-1].strip().split()[1].strip()
            phone = raw_data[3]
            hours_of_operation = ""
            for row in raw_data:
                if "0pm" in row or "0am" in row or "closed" in row.lower():
                    hours_of_operation = (hours_of_operation + " " + row).strip()
        store_number = "<MISSING>"
        location_type = ", ".join(list(val.ul.stripped_strings))
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        store = []
        store.append(locator_domain if locator_domain else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(base_url)
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
