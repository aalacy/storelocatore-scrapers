import csv
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    address = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.lexus.co.uk/"
    url = "https://www.lexus.co.uk/api/dealers/all"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    }
    response = session.get(url, headers=headers).json()
    j = response["dealers"]
    for i in j:
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(i["name"] if i["name"] else "<MISSING>")
        store.append(
            i["address"]["address1"].strip().replace("&#xD;&#xA;", " ")
            if i["address"]["address1"].strip()
            else "<MISSING>"
        )
        store.append(
            i["address"]["city"].strip()
            if i["address"]["city"].strip()
            else "<MISSING>"
        )
        store.append(
            i["address"]["region"].strip().replace("3", "<MISSING>")
            if i["address"]["region"].strip()
            else "<MISSING>"
        )
        store.append(i["address"]["zip"] if i["address"]["zip"] else "<MISSING>")
        store.append("UK")
        store.append(i["organisationCode"] if i["organisationCode"] else "<MISSING>")
        store.append(i["phone"] if i["phone"] else "<MISSING>")
        store.append(
            i["name"]
            .replace(i["address"]["city"], "")
            .strip()
            .replace("  ", " ")
            .replace("Battersea ", "")
            .replace(" Gatwick", "")
            .replace(" Isle of Man", "")
            .replace(" Woodford", "")
            if i["brand"]
            else "<MISSING>"
        )
        try:
            store.append(
                i["address"]["origin"]["lat"]
                if i["address"]["origin"]["lat"]
                else "<MISSING>"
            )
            store.append(
                i["address"]["origin"]["lon"]
                if i["address"]["origin"]["lon"]
                else "<MISSING>"
            )
        except:
            store.append("<MISSING>")
            store.append("<MISSING>")
        hours = ""
        if "WorkShop" in i["openingTimes"]:
            hour = i["openingTimes"]["WorkShop"]
            for k in hour:
                hours = hours + " " + k["day"] + " " + str(k["slots"])
            store.append(
                hours.replace("[{'openFrom': '", " ")
                .replace("', 'openTo': '", " - ")
                .replace("'}]", ", ")
                .replace("[]", "closed")
                if hours
                else "<MISSING>"
            )
        try:
            store.append(i["url"] if i["url"] else "<MISSING>")
        except:
            store.append("<MISSING>")
        if store[2] == "Hadfield Road":
            store.append("<MISSING>")
        if store[2] in address:
            continue
        address.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
