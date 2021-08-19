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


def get_store(soup2, page_url):
    main2 = soup2.find("div", {"class": "col-m-6"})

    if "Store Hours" not in str(main2):
        try:
            main2 = soup2.find_all("div", {"class": "col-m-6"})[1]
        except:
            main2 = soup2.find("div", {"class": "col-m-5"})

    loc = list(main2.stripped_strings)
    if "**New Address**" in loc:
        loc.remove("**New Address**")
        loc.remove("Store Location")

    hours = " ".join(loc[loc.index("Store Hours") :]).replace("Store Hours", "").strip()

    i = loc.index("Phone:")
    if i > 3:
        del loc[1]

    address = loc[1].strip()
    addr = loc[1].split(",")
    if len(addr) == 2 and i == 2:
        state = addr[-1].strip().split(" ")[0]
        zipp = addr[-1].strip().split(" ")[1]
        adr = addr[0].strip().split(" ")
        city = adr[-1].strip()
        del adr[-1]
        address = " ".join(adr)
        phone = loc[3].strip()
    else:
        ct = loc[2].split(",")

        city = ct[0].strip()
        state = ct[1].strip().split(" ")[0].strip()
        zipp = ct[1].strip().split(" ")[1].strip()
        phone = loc[4].strip()

    name = "Rockler " + city

    if "Suite 006-B" in address:
        address = "2000 Park Manor Blvd" + " " + loc[1]

    storeno = ""
    lat = (
        soup2.find("h3", text="Store Hours")
        .parent.parent.parent.find("iframe")["src"]
        .split("!3d")[1]
        .split("!")[0]
        .strip()
    )
    lng = (
        soup2.find("h3", text="Store Hours")
        .parent.parent.parent.find("iframe")["src"]
        .split("!2d")[1]
        .split("!")[0]
        .strip()
    )

    country = "US"

    store = []
    store.append("https://www.rockler.com")
    store.append(name if name else "<MISSING>")
    store.append(address if address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country if country else "<MISSING>")
    store.append(storeno if storeno else "<MISSING>")
    store.append(phone if phone else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat if lat else "<MISSING>")
    store.append(lng if lng else "<MISSING>")
    store.append(hours if hours.strip() else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    store = [str(x).strip() if x else "<MISSING>" for x in store]

    return store


def fetch_data():
    base_url = "https://www.rockler.com"
    return_main_object = []
    soup = BeautifulSoup(session.get(base_url + "/retail/stores").text, "lxml")

    for dt in soup.find("ul", {"class": "cms-menu"}).find_all("li")[:-1]:
        st = dt.find("a")["href"]

        req = session.get(st)
        soup1 = BeautifulSoup(req.text, "lxml")

        main1 = soup1.find("ul", {"class": "cms-menu"}).find_all("a")

        if not main1:
            soup2 = soup1
            page_url = req.url
            return_main_object.append(get_store(soup2, page_url))
        else:
            for dt1 in main1:
                page_url = dt1["href"]

                soup2 = BeautifulSoup(session.get(page_url).text, "lxml")
                return_main_object.append(get_store(soup2, page_url))

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
