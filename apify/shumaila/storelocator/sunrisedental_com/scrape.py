from bs4 import BeautifulSoup
import csv
import usaddress
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
    url = "https://sunrisedental.com/locations/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=dentist]")
    for div in divlist:

        title = div.text.strip().replace("\n", "")
        link = div["href"]
        if link.find("http") == -1:
            link = "https://sunrisedental.com" + link
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            address = soup.find("iframe")["title"].replace("United States", "").strip()
        except:
            continue
        phone = soup.find("small").text.strip()
        try:
            hours = soup.text.split("Monday:", 1)[1].splitlines()[0:7]
            hours = "Monday:" + " ".join(hours)
        except:
            hours = "<MISSING>"
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
        if len(pcode) < 3:
            pcode = "<MISSING>"
        state = state.replace("Washington", "WA")
        try:
            phone = phone.split("\n", 1)[0]
        except:
            pass
        if pcode == "9850":
            pcode = "98502"
        if len(state) < 2:
            try:
                city, state = (
                    soup.find("title")
                    .text.split("Top Dentist ", 1)[1]
                    .split(";", 1)[0]
                    .split(" ", 1)
                )
            except:
                if len(street) < 3 or "youtube Video Player" in street:
                    street = "<MISSING>"
                    state = "<MISSING>"
                    pcode = "<MISSING>"
                    city = "<MISSING>"
            state = state.split(" ", 1)[0]
        if "appointments" in phone:
            phone = "<MISSING>"
        if "E." in state:
            state = "WA"
            city = street
            street = "<MISSING>"
        data.append(
            [
                "https://sunrisedental.com/",
                link,
                title,
                street.replace(" o", ""),
                city,
                state.upper(),
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours.replace("\xa0", " ")
                .replace("pm", "pm ")
                .replace("  ", " ")
                .replace("Closed", "Closed ")
                .strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
