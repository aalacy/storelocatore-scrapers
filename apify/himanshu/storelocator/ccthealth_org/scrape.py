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
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    base_url = "https://ccthealth.org/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main = (
        soup.find("li", {"id": "menu-item-3572"})
        .find("ul", {"class": "sub-menu"})
        .find_all("a", {"itemprop": "url"})
    )
    for link in main:
        location_name = link.find("span", {"class": "avia-menu-text"}).text.strip()
        page_url = link["href"]
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")

        phone = list(
            soup1.find("h4", {"itemprop": "headline"}, text="Phone")
            .parent.parent.find("div", {"itemprop": "text"})
            .stripped_strings
        )
        phone = phone[0].replace("Phone:", "").split("/")[0].strip()
        if "478-862-9707" in phone:
            phone = "478-862-9707"
        hour = " ".join(
            list(
                soup1.find("h4", {"itemprop": "headline"}, text="Hours")
                .parent.parent.find("div", {"itemprop": "text"})
                .stripped_strings
            )
        )
        adr = list(soup1.find(class_="iconlist_content").stripped_strings)
        street_address = adr[0].split("Suite")[0]
        ct = adr[-1].split(",")
        city = ct[0].strip()
        st = ct[1].strip().split(" ")
        if len(st) == 2:
            state = st[0]
            zipp = st[1]
        else:
            try:
                zipp = int(ct[1])
                if city == "Cordele":
                    state = "GA"
                else:
                    state = "<MISSING>"
            except:
                state = ct[1]
                zipp = "<MISSING>"
        if "218 East Main Street" in street_address:
            street_address = "218 East Main Street"
            city = "Butler"
            state = "GA"
            zipp = "31006"
        try:
            latitude = (
                soup1.find("script", {"class": "av-php-sent-to-frontend"})
                .text.split("av_google_map['0']['marker']['0']['long'] =")[1]
                .split(";")[0]
                .strip()
            )
            longitude = (
                soup1.find("script", {"class": "av-php-sent-to-frontend"})
                .text.split("av_google_map['0']['marker']['0']['lat'] =")[1]
                .split(";")[0]
                .strip()
            )
        except:
            latitude = ""
            longitude = ""
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hour)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
