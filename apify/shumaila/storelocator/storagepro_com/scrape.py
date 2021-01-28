from bs4 import BeautifulSoup
import csv
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headers1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "Connection": "keep-alive",
    "Host": "tenantapi.com",
    "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjI4MDczNjkiLCJhcCI6IjgyNzU0OTI1OSIsImlkIjoiZjdhOWZkMjg0ZWVlODllZSIsInRyIjoiM2I4ZTkxMGZmNDQ4YWEwOTY5NDIyYjg5YTdhN2Q1MzAiLCJ0aSI6MTYwNTg3MTQzNzgyM319",
    "Origin": "https://www.storagepro.com",
    "Referer": "https://www.storagepro.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "X-storageapi-date": "1609072757",
    "X-storageapi-key": "8651844f76294d9f9ce61ac39ae0d33f",
    "X-storageapi-trace-id": "9b92861f-fb2e-4afe-89d1-fb8727e82b9e",
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
    p = 0
    data = []
    titlelist = []
    for k in range(0, 2):
        if k == 0:
            zips = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
        elif k == 1:
            zips = static_zipcode_list(
                radius=100, country_code=SearchableCountries.CANADA
            )
        for zip_code in zips:

            url = (
                "https://tenantapi.com/v3/applications/app72d8cb0233044f5ba828421eb01e836b/v1/search/owners/own3635fb2e825d49a9a7a9f8d9bcdcd304/?&lat=&lon=&ip=&address="
                + zip_code
                + "&state=&filter_storage_type=undefined&filter_unit_size=&list_all=true"
            )
            loclist = session.get(url, headers=headers1, timeout=5).json()[
                "applicationData"
            ]["app72d8cb0233044f5ba828421eb01e836b"][0]["data"]

            for loc in loclist:
                link = loc["landing_page_url"]
                if link in titlelist:
                    continue
                titlelist.append(link)
                store = loc["id"]
                title = loc["name"]
                street = loc["address"]["street_address"]
                city = loc["address"]["city"]
                state = loc["address"]["state"]
                pcode = loc["address"]["zipcode"]
                phone = loc["phone"][0]["number"]
                try:
                    phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
                except:
                    phone = "<MISSING>"
                lat = loc["geolocation"]["latitude"]
                longt = loc["geolocation"]["longitude"]
                try:
                    r = session.get(link, headers=headers, timeout=5)
                    soup = BeautifulSoup(r.text, "html.parser")
                    link = r.url
                    try:
                        hours = soup.find("div", {"class": "office-hours"}).text
                    except:
                        hours = "<MISSING>"
                except:
                    link = "<MISSING>"
                    hours = "<MISSING>"
                ltype = "Store"
                if link.find("storagepro.com") == -1:
                    ltype = "Facility Partner"
                ccode = "US"
                if pcode.isdigit():
                    pass
                else:
                    ccode = "CA"
                if len(hours) < 3:
                    hours = "<MISSING>"
                if len(phone) < 3:
                    phone = "<MISSING>"
                data.append(
                    [
                        "https://www.storagepro.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        store,
                        phone,
                        ltype,
                        lat,
                        longt,
                        hours.replace("AM", " AM ")
                        .replace("PM", " PM ")
                        .replace("Closed", "Closed "),
                    ]
                )

                p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
