import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    r = session.get("https://www.canyonranch.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    addresses = []
    for location in soup.find("ul", {"id": "menu-main-menu"}).find_all("a"):
        tempname = location.text.replace("Wellness Resort", "").replace(
            "Wellness Retreat", ""
        )
        link = location["href"] + "plan-your-visit/"
        location_request = session.get(link, headers=headers)
        location_detail_soup = BeautifulSoup(location_request.text, "html.parser")
        hourslist = location_detail_soup.text.splitlines()
        hours = ""
        for hr in hourslist:
            if " am " in hr and " pm " in hr:
                hours = hours + hr + " "
        geo_request = session.get(
            location_detail_soup.find_all("iframe")[-1]["src"], headers=headers
        )

        phone = location_request.text.split('"tel:+', 1)[1].split('"', 1)[0]
        try:
            content = geo_request.text.split(
                '0,[["0x80c8c43e7c50b86b:0x7067f11051bb7ef8"', 1
            )[1].split(',"8099707507242139384"],', 1)[0]
            content = content.replace('"', "").strip().split(",")
            phone = geo_request.text.split('"tel:+', 1)[1].split('"', 1)[0]
            hours = "Open daily from 6 am to 8 pm"
            name = content[1]
        except:
            pass
        try:
            lat = content[5].replace("[", "")
            lng = content[6].replace("]", "")
        except:
            lat = lng = "<MISSING>"
        try:
            state_split = content[4]
            if state_split:
                state, store_zip = state_split.strip().split(" ", 1)
        except:
            state = tempname.split(", ")[1]
            store_zip = "<MISSING>"
        try:
            city = content[3]
        except:
            city = tempname.split(", ")[0]
        store = []
        store.append("https://www.canyonranch.com")
        store.append(location["href"])
        try:
            store.append(name.replace("–", "-"))
        except:
            store.append(tempname)
        try:
            store.append(content[2])
        except:
            store.append("<MISSING>")
        if len(hours) < 3:
            hours = "<MISSING>"
        addresses.append(store[-1])
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("canyon ranch")
        try:
            store.append(lat)
        except:
            store.append("<MISSING>")
        try:
            store.append(lng)
        except:
            store.append("<MISSING>")
        store.append(hours.replace("Hours: ", ""))
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
