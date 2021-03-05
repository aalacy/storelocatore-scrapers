import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    base_url = "https://www.altamed.org/"
    page = 1
    for i in range(20):
        page_url = "https://www.altamed.org/find/facility?page=" + str(page)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        stores = soup.find_all("div", {"class": "clinic-wrapper altamed-type"})
        if len(stores) == 0:
            break
        for data in stores:
            location_name = data.find("h3", {"class": "altamed-type"}).text
            if location_name == "AltaMed Medical Group -":
                continue
            addr = data.find("div", {"class": "address"}).find("p").text
            street_address = addr.split(",")[0].split("Ste")[0].strip()
            city = addr.split(",")[-2]
            state = addr.split(",")[-1].split()[0]
            zipp = addr.split(",")[-1].split()[1]
            phone = data.find("div", {"class": "phone"}).text.strip()
            if data.find("div", {"class": "specialties"}):
                location_type = data.find("div", {"class": "specialties"}).text.strip()
            else:
                location_type = "<MISSING>"
            hours = ""
            for day in data.find_all("div", {"class": "col-xs-6 col-sm-3"}):
                hours += " " + " ".join(list(day.stripped_strings))
            hours = hours

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            store.append(page_url)
            store = [str(x).strip() if x else "<MISSING>" for x in store]

            yield store
        page += 1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
