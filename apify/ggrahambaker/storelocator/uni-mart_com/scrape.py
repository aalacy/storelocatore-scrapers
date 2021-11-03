from sgrequests import SgRequests
import re
import csv

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://uni-mart.com/locations"
    p = 0
    mydata = {
        "searchzip": "Pensylvania",
        "task": "search",
        "radius": "-1",
        "limit": "0",
        "option": "com_mymaplocations",
        "component": "com_mymaplocations",
        "Itemid": "223",
        "zoom": "9",
        "limitstart": "0",
        "format": "json",
        "geo": "",
        "latitude": "",
        "longitude": "",
    }

    loclist = session.post(url, data=mydata, headers=headers).json()["features"]
    for loc in loclist:
        longt = loc["geometry"]["coordinates"][0]
        lat = loc["geometry"]["coordinates"][1]
        title = loc["properties"]["name"]
        link = "https://uni-mart.com" + loc["properties"]["url"]
        content = loc["properties"]["fulladdress"]
        content = re.sub(cleanr, "\n", str(content)).strip().splitlines()
        street = content[0]
        city, state = content[1].split("&#44;", 1)
        pcode = content[2].split("&nbsp;", 1)[1]
        store = title.split("#")[1]
        hours = "<MISSING>"
        data.append(
            [
                "https://uni-mart.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                "<MISSING>",
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


if __name__ == "__main__":
    scrape()
