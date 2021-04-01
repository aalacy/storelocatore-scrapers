import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import unicodedata

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
    base_url = "https://www.firstbankonline.com/location/?type=branches"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    k = soup.find("div", {"class": "block stdblock branch-block"}).find_all(
        "div", {"class": "branch"}
    )
    for i in k:
        adr = list(i.stripped_strings)
        name = adr[0]
        adr1 = ""
        location_type = "branche"
        page_url = i.find("a", {"class": "btn info"})["href"]
        soup1 = BeautifulSoup(session.get(page_url).text, "lxml")
        lat = (
            str(soup1)
            .split("] = new google.maps.LatLng(")[1]
            .split(");")[0]
            .split(",")[0]
        )
        lng = (
            str(soup1)
            .split("] = new google.maps.LatLng(")[1]
            .split(");")[0]
            .split(",")[1]
        )
        try:
            hours = " ".joinlist(soup1.find("div", {"class": "hrs"}).stripped_strings)
        except:
            hours = "<MISSING>"
        for index, c in enumerate(adr):
            if "Call" in c:
                adr1 = adr[index:]
        for index, c in enumerate(adr):
            if "Call" in c:
                adr = adr[:index]
        city = adr[-1].split(",")[0]
        state = adr[-1].split(",")[-1].split()[0]
        zipcode = adr[-1].split(",")[-1].split()[1]
        street_address = " ".join(adr[1:-1]).replace(",", "")
        if "1015 Westhaven" in street_address:
            city = "Franklin"
            state = "TN"
            zipcode = "37064"

        phone = adr1[0].replace("Call ", "")

        tem_var = []
        tem_var.append("https://www.firstbankonline.com/")
        tem_var.append(name.replace("�", ""))
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours.replace("Hours: ", ""))
        tem_var.append(page_url)
        for i in range(len(tem_var)):
            if isinstance(tem_var[i], str):
                tem_var[i] = "".join(
                    (
                        c
                        for c in unicodedata.normalize("NFD", tem_var[i])
                        if unicodedata.category(c) != "Mn"
                    )
                )
        tem_var = [x.replace("–", "-") if isinstance(x, str) else x for x in tem_var]
        tem_var = [str(x).strip() if x else "<MISSING>" for x in tem_var]
        yield tem_var

    base_url = "https://www.firstbankonline.com/location/?type=atm"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    k = soup.find("div", {"class": "block stdblock branch-block"}).find_all(
        "div", {"class": "branch"}
    )
    for i in k:
        adr = list(i.stripped_strings)
        name = adr[0]
        city = adr[-3].split(",")[0]
        state = adr[-3].split(",")[-1].split()[0]
        zipcode = adr[-3].split(",")[-1].split()[1]
        hours = " ".join(adr[-2:-1])
        street_address = " ".join(adr[1:-3]).replace(",", "")
        if "1015 Westhaven" in street_address:
            city = "Franklin"
            state = "TN"
            zipcode = "37064"

        location_type = "ATM"
        page_url = "<MISSING>"
        tem_var = []
        tem_var.append("https://www.firstbankonline.com/")
        tem_var.append(name.replace("�", ""))
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zipcode.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(location_type)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours.replace("Hours: ", ""))
        tem_var.append(page_url)
        for i in range(len(tem_var)):
            if isinstance(tem_var[i], str):
                tem_var[i] = "".join(
                    (
                        c
                        for c in unicodedata.normalize("NFD", tem_var[i])
                        if unicodedata.category(c) != "Mn"
                    )
                )
        tem_var = [x.replace("–", "-") if isinstance(x, str) else x for x in tem_var]
        tem_var = [str(x).strip() if x else "<MISSING>" for x in tem_var]
        yield tem_var


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
