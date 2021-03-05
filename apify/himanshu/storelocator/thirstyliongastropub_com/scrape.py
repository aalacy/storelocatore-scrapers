import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

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
    base_url = "https://www.thirstyliongastropub.com/"

    soup = bs(
        session.get("https://www.thirstyliongastropub.com/addresses").text, "lxml"
    )

    for row in soup.find(
        "div", {"class": "sqs-layout sqs-grid-12 columns-12"}
    ).find_all("div", {"class": "sqs-block html-block sqs-block-html"}):

        addr = list(row.stripped_strings)
        if len(addr) < 2:
            continue

        if "," in addr[1]:
            if len(addr[1].split(",")) == 2:
                street_address = (
                    " ".join(addr[1].split(",")[0].split()[:-1])
                    .replace("|", "")
                    .strip()
                )
                city = addr[1].split(",")[0].split()[-1]

            else:
                street_address = (
                    addr[1].split(",")[0]
                    + " "
                    + " ".join(addr[1].split(",")[1].split()[:-1])
                    .replace("|", "")
                    .strip()
                )
                city = addr[1].split(",")[1].split()[-1]

            state = addr[1].split(",")[-1].split()[0]
            zipp = addr[1].split(",")[-1].split()[1]
            del addr[:3]

        else:
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].split()[0]
            zipp = addr[2].split(",")[1].split()[1]
            del addr[:4]
        phone = addr[-1]

        del addr[-2:]
        hours = " ".join(addr)

        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Thirsty Lion Gastropub & Grill")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append("https://www.thirstyliongastropub.com/addresses")
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
