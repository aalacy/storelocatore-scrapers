import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()


def preprocess(row):
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
        "Alberta",
        "British Columbia",
        "Manitoba",
        "New Brunswick",
        "Newfoundland and Labrador",
        "Northwest Territories",
        "Nova Scotia",
        "Nunavut",
        "Ontario",
        "Prince Edward Island",
        "Quebec",
        "Saskatchewan",
        "Yukon",
    ]
    raw_address = row[-1]
    row[2] = raw_address.split(",")[0]
    if row[2] == "<INACCESSIBLE>":
        row[2] = "<MISSING>"

    zip1 = re.findall(r"[0-9]+", raw_address)
    zip2 = re.findall(r"[A-Z]\d[A-Z] *\d[A-Z]\d", raw_address)
    for z in zip1:
        if len(z) == 5:
            row[5] = str(z).replace("[", "").replace("]", "").replace(",", "")
    if zip2 != []:
        row[5] = str(zip2).replace("[", "").replace("]", "").replace(",", "")
    if row[5] == "<INACCESSIBLE>":
        row[5] = "<MISSING>"

    v = raw_address.split(",")[1:]
    if len(v) >= 3:
        city = re.findall(r"[A-Za-z]+\s[A-Za-z]+|[A-Za-z]+", v[0])
        if city != []:
            row[3] = city[0]
    else:
        if row[3] == "<INACCESSIBLE>":
            row[3] = "<MISSING>"

    lst = raw_address.split(",")
    for l in lst:
        l = l.strip()
        state = re.findall(r"[A-Z]{2}", l)
        if state != []:
            row[4] = state[0]
        else:
            if l in states:
                row[4] = l[0]
    if row[4] == "<INACCESSIBLE>":
        row[4] = "<MISSING>"
    return row[0:-1]


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
            r = preprocess(row)
            writer.writerow(r)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://f45training.com"
    r = session.get("https://f45training.com/find-a-studio/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    scripts = soup.find_all("script")
    for script in scripts:
        if "window.domains" in script.text:
            location_list = json.loads(
                script.text.split("window.studios = ")[1].split("}]};")[0] + "}]}"
            )["hits"]
            for i in range(len(location_list)):
                current_store = location_list[i]
                store = []
                store.append("https://f45training.com")
                store.append(current_store["name"])
                if current_store["location"] == "":
                    continue
                if current_store["country"] == "United States":
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("US")
                elif current_store["country"] == "Canada":
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append("CA")
                else:
                    continue
                store.append(current_store["id"])
                location_request = session.get(
                    "https://f45training.com/" + current_store["slug"], headers=headers
                )
                location_soup = BeautifulSoup(location_request.text, "lxml")
                if location_soup.find("a", {"href": re.compile("tel:")}) is None:
                    phone = "<MISSING>"
                else:
                    phone = location_soup.find("a", {"href": re.compile("tel:")}).text

                store.append(
                    phone.split("/")[0].split(",")[0].replace("(JF45)", "")
                    if phone != ""
                    else "<MISSING>"
                )
                store.append("f45")
                store.append(current_store["_geoloc"]["lat"])
                store.append(current_store["_geoloc"]["lng"])
                store.append("<MISSING>")
                store_link = (
                    current_store["name"].split(" ")[1].replace(" ", "").lower()
                )
                store.append(base_url + "/" + store_link + "/home")
                store.append(current_store["location"])
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
