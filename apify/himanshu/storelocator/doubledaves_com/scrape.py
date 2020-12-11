import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
    addressess = []
    base_url = "https://www.doubledaves.com"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    main = soup.find("div", {"class": "dropdown location-dropdown"}).find_all("a")
    del main[-1]
    for atag in main:
        r1 = session.get(base_url + atag["href"])
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1 = soup1.find("div", {"class": "location-grid"}).find_all(
            "a", text="Website"
        )
        for weblink in main1:
            r2 = session.get(base_url + weblink["href"])
            page_url = base_url + weblink["href"]
            soup2 = BeautifulSoup(r2.text, "lxml")
            main2 = soup2.find("div", {"class": "location-hours"}).find_all("p")
            if len(main2) == 2:
                loc_address = list(main2[1].stripped_strings)
                phone = main2[0].text.strip()
            else:
                loc_address = list(main2[0].stripped_strings)
                phone = "<MISSING>"
            address = loc_address[0].strip()
            city = loc_address[1].strip().split(",")[0].strip()
            state = loc_address[1].strip().split(",")[1].strip().split(" ")[0].strip()
            zip = loc_address[1].strip().split(",")[1].strip().split(" ")[1].strip()
            if soup2.find("div", {"class": "hours grid-cell"}):
                mainhour = soup2.find("div", {"class": "hours grid-cell"}).find_all(
                    "div", {"class": "grid no-wrap desktop-collapse only-desktop"}
                )
                title = list(mainhour[0].stripped_strings)
                h = ""
                h1 = ""
                head = title[0]
                if len(title) == 2:
                    head2 = title[1]
                del mainhour[0]
                for hr in mainhour:
                    hr1 = list(hr.stripped_strings)
                    h += hr1[0] + ":" + hr1[1] + " "
                    if len(title) == 2:
                        if len(hr1) == 3:
                            h1 += hr1[0] + ":" + hr1[2] + " "
                hour = head + " = " + h
                if len(title) == 2:
                    hour += hour + head2 + " = " + h1
            else:
                hour = "<MISSING>"

            store = []
            store.append("https://www.doubledaves.com/")
            store.append(
                soup2.find("div", {"class": "page-heading"}).find("h1").text.strip()
            )
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("DoubleDave's Pizzaworks")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hour.replace("Dough Slingin' Hours = ", "").replace("::", " "))
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
