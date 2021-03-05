import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

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
    url = "https://www.pridestores.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax"
    querystring = {
        "gridAppId": "a5534314-58bf-4aee-aa37-7081ab10004e",
        "instance": "wixcode-pub.c080237ec7458a0cd208bcdf4cd9c3547b5db48c.eyJpbnN0YW5jZUlkIjoiYTRkMTY0MzctN2FlOC00NjhlLWIyZjEtMjZjOWNhYTM2Yzg0IiwiaHRtbFNpdGVJZCI6IjAzNDgyY2Y0LWQxNTQtNDM4OC1hMDIzLTk0NGYzZjNlOGE3ZSIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYwMjU3Mzg5ODA4MywiYWlkIjoiMjRiNzA4NzktM2FmMi00MjJjLThkODktYjFkMmRlZGQ5NDNiIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImJmNDc3NDBiLTMwMTAtNGY4Yy05YzI4LWY0NmE4MjYzNjNhYyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsSGFzRG9tYWluLFNob3dXaXhXaGlsZUxvYWRpbmciLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiMzY1ZTJhNjAtOGNlZS00ZDMwLWE0YTYtOWIyNTQ0NDRhYzNmIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==",
        "viewMode": "site",
    }
    payload = '["Locations",null,[{"city":"asc"}],0,32,null,null]'
    API_headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "x-xsrf-token": "1602573509|I_OES7OmIT2s",
        "content-type": "application/json",
        "cache-control": "no-cache",
    }

    APICall = session.post(
        url, data=payload, headers=API_headers, params=querystring
    ).json()

    for api in APICall["result"]["items"]:

        page_url = "https://www.pridestores.com" + api["url"].lower()

        street_address = api["address"]

        city = api["city"]
        phone = api["phone"]

        hours = (
            "Mon - Fri: "
            + api["hours"]
            + " Saturday: "
            + api["satHours"]
            + " Sunday: "
            + api["sunHours"]
        )

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        }
        location_soup = bs(session.get(page_url, headers=headers).text, "html5lib")
        location_name = location_soup.find_all("h2", {"class": "font_2"})[0].text
        if location_soup.find("div", {"class": "_1Z_nJ"}):
            if "/ss" in page_url or "/agw" in page_url:

                addr = list(
                    location_soup.find_all("div", {"class": "_1Z_nJ"})[
                        0
                    ].stripped_strings
                )
            else:

                addr = list(
                    location_soup.find_all("div", {"class": "_1Z_nJ"})[
                        1
                    ].stripped_strings
                )
        else:
            if "bel" in page_url:

                addr = list(
                    location_soup.find_all(
                        "div", {"class": "txtNew", "data-packed": "true"}
                    )[0].stripped_strings
                )
            else:
                addr = list(
                    location_soup.find_all(
                        "div", {"class": "txtNew", "data-packed": "true"}
                    )[1].stripped_strings
                )

        city = addr[0].split(",")[1].strip().replace("MA", "Springfield")
        if len(addr[0].split(",")) == 3:
            state = addr[0].split(",")[-1].strip()
        else:
            state = "MA"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        zipp = "<MISSING>"
        store = []
        store.append("https://pridestores.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Pride Stores")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append("https://www.pridestores.com/stores")
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
