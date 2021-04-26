import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://viewer.blipstar.com/searchdbnew?uid=2483677&lat=34.09010&lng=-118.40650&type=nearest&value=10000&keyword=&max=10000&sp=90210,%20CA&ha=no&htf=1&son=&product=false&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.9870351849532255"
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for x in range(1, len(array)):
        store = array[x]["n"]
        state = array[x]["s"]
        add = array[x]["a"].split("<")[0].strip()
        try:
            city = (
                array[x]["a"].split("<span class='storecity'>")[1].split("<")[0].strip()
            )
        except:
            city = "<MISSING>"
        zc = array[x]["pc"]
        try:
            phone = array[x]["p"]
        except:
            phone = "<MISSING>"
        country = "US"
        typ = "Restaurant"
        website = "ljsilvers.com"
        lat = array[x]["lat"]
        lng = array[x]["lng"]
        hours = "<MISSING>"
        name = "Long John Silver's"
        loc = "<MISSING>"
        yield [
            website,
            loc,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
