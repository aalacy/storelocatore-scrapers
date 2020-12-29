import csv
import usaddress
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    data = []
    url = "https://mistercarwash.com/locations/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split("var markers = ")[1].split("}]")[0]
    r = r + "}]"
    loclist = json.loads(r)
    for loc in loclist:
        title = loc["name"]
        store = loc["loc_id"]
        lat = loc["lat"]
        longt = loc["lng"]
        address = (
            loc["address"]
            .replace(", ", " ")
            .replace("United States", "")
            .replace("USA", "")
            .replace("Rd", "Rd.")
            .strip()
        )

        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")
        hours = loc["loc_hours"]
        try:
            phone = str(loc["infoContent"]).split("Phone:</b>", 1)[1].split("<", 1)[0]
        except:
            phone = "<MISSING>"
        try:
            state = state.strip().split(" ", 1)[0]
        except:
            pass
        try:
            state = state.split(",", 1)[0]
        except:
            pass
        if len(pcode) < 3:
            pcode = "<MISSING>"
        if len(phone) < 3 or "Car Wash" in phone:
            phone = "<MISSING>"
        if len(hours) < 3 or "Car Wash:" in hours:
            hours = "<MISSING>"
        if state == "" and "Comstock Park MI" in address:
            state = "MI"
            city = "Comstock Park"
        if "Kennewick" in city:
            state = "WA"
        if len(state) < 2:
            state = city.split(" ")[-1].strip()
            if len(state) == 2:
                city = city.replace(state, "").strip()
            else:
                state = "<MISSING>"
        if "<MISSING>" in state:
            state = street.split(" ")[-1].strip()
            if len(state) == 2:
                street = street.replace(state, "").strip()
                city = street.split(" ")[-1].strip()
                if "Land" or "Shoals" in city:
                    city = street.split(" ")[-2].strip() + " " + city
                street = street.replace(city, "").strip()
            else:
                state = "<MISSING>"
        if len(city) < 2:
            city = "<MISSING>"
        try:
            hours = hours.split("/", 1)[0]
        except:
            pass
        if "Georgia" in state:
            state = "GA"
        if "Austin" in city:
            state = "TX"
        if title.find("Coming Soon") == -1:
            data.append(
                [
                    "https://mistercarwash.com",
                    "https://mistercarwash.com/locations/",
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
