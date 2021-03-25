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
    base_url = "https://www.properhotel.com"
    return_main_object = []
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    locs = soup.find(class_="arrownav-hotellist").find_all("a")
    for dt in locs:
        page_url = dt["href"]
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        city = dt.text.strip()
        main1 = soup1.find("div", {"class": "ftr-address"})
        if soup1.find("div", {"class": "ftr-address"}) is not None:
            loc = list(main1.stripped_strings)
            storeno = ""
            lt = main1.find("a", alt="Map Marker")["href"].split("@")[1].split(",")
            country = "US"
            address = loc[1]
            if "," in loc[2]:
                city_line = loc[2].split(",")
            else:
                city_line = loc[3].split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zipp = city_line[-1].strip().split()[1].strip()
            lat = lt[0]
            lng = lt[1]

            phone = "<MISSING>"
            for i, row in enumerate(loc):
                if "front desk" in row.lower():
                    phone = loc[i + 1]
                    break
            store = []
            store.append(base_url)
            store.append(loc[0])
            store.append(
                address.replace("Entrance at ", "") if address else "<MISSING>"
            )
            store.append(city)
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            if (
                "Accepting Reservations – Starting"
                in soup1.find(class_="mainwelcome-content").text
            ):
                loc_type = "Coming Soon"
            else:
                loc_type = "Open"
            store.append(loc_type)
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
