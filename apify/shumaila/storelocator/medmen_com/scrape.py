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
    p = 0
    headers = {
        "Sec-Fetch-Mode": "cors",
        "Origin": "https://www.medmen.com",
        "X-Contentful-User-Agent": "sdk contentful.js/0.0.0-determined-by-semantic-release; platform browser; os macOS;",
        "Authorization": "Bearer 3a1fbd8bd8285a5ebe9010b17959d62fed27abc42059373f3789023bb7863a06",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.medmen.com/stores",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "DNT": "1",
    }
    params = (("content_type", "store"),)
    storeslist = session.get(
        "https://cdn.contentful.com/spaces/1ehd3ycc3wzr/environments/master/entries",
        headers=headers,
        params=params,
    ).json()["items"]
    for store in storeslist:
        store = store["fields"]
        if "comingSoon" not in store.keys() or not store["comingSoon"]:
            link = "https://www.medmen.com/stores/" + store["slug"]
            location_id = store["securityId"]
            title = store["name"]
            street = store["address"]
            city = store["county"]
            try:
                pcode = store["address2"].split(" ")[-1]
            except:
                pcode = "<MISSING>"
            state = store["state"]
            phone = store["phoneNumber"]
            lat = store["location"]["lat"]
            longt = store["location"]["lon"]
            hours = store["storeHours"]
            try:
                if "Sun " in store["storeHours2"]:
                    hours = hours + " " + store["storeHours2"]
            except:
                pass
            if location_id.isdigit():
                pass
            else:
                location_id = "<MISSING>"
            data.append(
                [
                    "https://www.medmen.com",
                    link,
                    title,
                    street.replace('"', ""),
                    city.replace('"', ""),
                    state.replace(",", "").replace('"', ""),
                    pcode.replace('"', ""),
                    "US",
                    location_id,
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
