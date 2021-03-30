import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ginoseast_com")


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    r = session.get("https://www.ginoseast.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for data in soup.find("div", {"id": "page-5db3337c9f175d60ba85158a"}).find_all(
        "h3"
    ):
        for link in data.find_all("a"):
            page_url = "https://www.ginoseast.com" + link["href"]
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            name = soup1.h1.text.strip()
            full = list(
                soup1.find_all("div", {"class": "col sqs-col-6 span-6"})[1]
                .find("div", {"class": "row sqs-row"})
                .stripped_strings
            )
            phone = full[-1]
            if "coming soon" in phone.lower():
                continue

            try:
                city = full[-3].split(",")[0]
            except:
                city = "<MISSING>"

            try:
                state = full[-3].split(",")[1].strip().split()[0]
            except:
                state = "<MISSING>"

            try:
                zipcode = full[-3].split(",")[1].strip().split()[-1]
            except:
                zipcode = "<MISSING>"

            if zipcode == "60665":
                zipcode = "60605"
            street = full[-4]
            hours = " ".join(full[1:-5])
            if not hours:
                hours = "<MISSING>"
            store = []
            store.append("https://www.ginoseast.com")
            store.append(name)
            store.append(street)
            store.append(city)
            store.append(state)
            store.append(zipcode.replace("CA", "<MISSING>"))
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(
                hours.replace("Delivery & Curbside Pick-Up available ", "").replace(
                    " Delivery available after 5pm", ""
                )
            )
            store.append(page_url)

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
