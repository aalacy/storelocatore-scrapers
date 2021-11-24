import csv
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
    url = "https://www.godivachocolates.co.uk/plugin/godivauk/finding-nearest-shops"
    for i in range(1, 4):
        myobj = {"type": str(i)}
        loclist = session.post(url, headers=headers, data=myobj, verify=False).json()[
            "data"
        ]["data"]
        for loc in loclist:
            store = loc["id"]
            loc = loc["data"]
            title = loc["name"]
            phone = loc["phone"]
            hours = loc["working_hours"]
            if i == 1:
                ltype = "Store"
            elif i == 2:
                ltype = "Concession"
            elif i == 3:
                ltype = "Cafe"
            street = loc["address"].split("\n")[0]
            city = "<MISSING>"

            if len(loc["address"].split("\n")) > 1:
                if len(loc["address"].split("\n")[1].split(" ")) > 2:
                    city = " ".join(loc["address"].split("\n")[1].split(" ")[2:])
                if len(loc["address"].split("\n")) > 2:
                    city = loc["address"].split("\n")[2]
                if len(loc["address"].split("\n")[1].split(" ")) < 1:
                    city = loc["address"].split("\n")[1]
            else:
                city = "<MISSING>"
            if "Email" in city:
                city = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            lat = loc["latitude"]
            longt = loc["longitude"]
            if lat == "":
                lat = "<MISSING>"
            if longt == "":
                longt = "<MISSING>"
            pcode = loc["postcode"]
            hours = loc["working_hours"]
            if pcode == "" or title == "Meadowhall":
                pcode = " ".join(loc["address"].split("\n")[1].split(" ")[0:2])
            link = "https://www.godivachocolates.co.uk/stores?ca_shop_type=" + str(i)
            data.append(
                [
                    "https://www.godivachocolates.co.uk",
                    link,
                    title,
                    street.rstrip().rstrip(",").strip("\n"),
                    city.rstrip().rstrip(",").strip("\n"),
                    "<MISSING>",
                    pcode,
                    "UK",
                    store,
                    phone,
                    ltype,
                    lat,
                    longt,
                    hours,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
