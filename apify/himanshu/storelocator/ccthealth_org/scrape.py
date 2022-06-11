import csv

from bs4 import BeautifulSoup

from lxml import html

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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

    soup = BeautifulSoup(r.text, "html.parser")
    main = (
        soup.find("li", {"id": "menu-item-3572"})
        .find("ul", {"class": "sub-menu"})
        .find_all("a", {"itemprop": "url"})
    )
    for link in main:
        location_name = link.find("span", {"class": "avia-menu-text"}).text.strip()
        page_url = link["href"]
        r1 = session.get(page_url, headers=headers)
        tree = html.fromstring(r1.text)
        soup1 = BeautifulSoup(r1.text, "html.parser")

        try:
            a = list(
                soup1.find("h4", {"itemprop": "headline"}, text="Phone")
                .parent.parent.find("div", {"itemprop": "text"})
                .stripped_strings
            )

            phone = a[0].replace("Phone:", "").split("/")[0].strip()
            if "478-862-9707" in phone:
                phone = "478-862-9707"
            if phone.find("Tel") != -1:
                phone = "".join(a[1]).strip()
        except:
            try:
                phone = (
                    soup1.find(id="av-layout-grid-1")
                    .find_all("section")[1]
                    .a.text.strip()
                )
            except:
                phone = (
                    soup1.find_all(class_="iconbox_content_container")[1]
                    .text.replace("Phone:", "")
                    .strip()
                )

        try:
            hour = " ".join(
                list(
                    soup1.find("h4", {"itemprop": "headline"}, text="Hours")
                    .parent.parent.find("div", {"itemprop": "text"})
                    .stripped_strings
                )
            )
        except:
            try:
                hours = (
                    soup1.find(id="av-layout-grid-1")
                    .find_all("section")[1]
                    .find_all("p")[2:]
                )
                hour = ""
                for row in hours:
                    hour = (hour + " " + row.get_text()).strip()
            except:
                hour = soup1.find_all(class_="iconbox_content_container")[
                    2
                ].text.strip()

        if "8300 Open" in hour:
            hour = hour.split("8300")[1].strip()

        try:
            adr = list(soup1.find(class_="iconlist_content").stripped_strings)
        except:
            try:
                adr = list(
                    soup1.find(id="av-layout-grid-1")
                    .find_all("section")[1]
                    .p.stripped_strings
                )
            except:
                adr = list(
                    soup1.find_all(class_="iconbox_content_container")[
                        0
                    ].stripped_strings
                )

        street_address = adr[0].split("Suite")[0].replace(",", "")
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
        if "1909 US Hwy" in street_address:
            city = "Tifton"
            state = "GA"
            zipp = "31793"

        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split("lat'] = ")[1]
                .split(";")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split("long'] = ")[1]
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

    # School clinics
    school_hours_url = "https://ccthealth.org/careconnect-school-clinics-butler/"

    r1 = session.get(school_hours_url, headers=headers)
    soup1 = BeautifulSoup(r1.text, "html.parser")

    hour = ""
    rows = soup1.find_all(class_="iconlist_content")
    for row in rows:
        if "day" in row.text.lower():
            hour = row.text
            break

    page_url = "https://ccthealth.org/locations-school-clinics/"

    r1 = session.get(page_url, headers=headers)
    soup1 = BeautifulSoup(r1.text, "html.parser")

    items = soup1.find_all(class_="av_textblock_section")
    for i in items:
        item = list(i.stripped_strings)
        location_name = item[0]
        street_address = item[1]
        city_line = item[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zipp = city_line[-1].strip().split()[1].strip()
        phone = item[3].replace("Telephone:", "").strip()
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
        store.append(school_hours_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
