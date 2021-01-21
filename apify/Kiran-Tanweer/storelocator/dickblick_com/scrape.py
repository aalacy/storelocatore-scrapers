from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dickblick_com")

session = SgRequests()
headers = {
    "authority": "api.dickblick.com",
    "method": "GET",
    "path": "/contentprovider/api/v2.0/StorePage/",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "if-modified-since": "Sun, 10 Jan 2021 15:49:10 GMT",
    "newrelic1": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE0MTA4MDQiLCJhcCI6IjMwNjQ2NjQyNSIsImlkIjoiZDY4YWE5MDk3MGIzMzU5YyIsInRyIjoiMWIzYTIwYjBkMDFiY2U0N2U4MGY1NmNlYWYwNDM2NjAiLCJ0aSI6MTYxMDI5NDc2NjAyMH19",
    "origin": "https://www.dickblick.com",
    "referer": "https://www.dickblick.com/stores/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "shopperid": "0AA39DB798B34A9C89F42CA6BD9396D2",
    "traceparent": "00-1b3a20b0d01bce47e80f56ceaf043660-d68aa90970b3359c-01",
    "tracestate": "1410804@nr=0-1-1410804-306466425-d68aa90970b3359c----1610294766020",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    hoo = ""
    url = "https://api.dickblick.com/contentprovider/api/v2.0/StorePage/"
    r = session.get(url, headers=headers, verify=False).json()
    for store in r:
        page = "https://www.dickblick.com" + store["storeUrl"]
        if page != "https://www.dickblick.com/stores/california/san-francisco-soma/":
            phone = store["store"]["phoneNumber"]
        else:
            phone == "<MISSING>"
        storeid = store["storeNumber"]
        storename = store["storeName"]
        street = store["store"]["addressLine1"]
        city = store["store"]["city"]
        state = store["store"]["statePicker"]["stateAbbreviation"]
        pcode = store["store"]["zipCode"]
        lat = store["store"]["coordinates"]["lat"]
        lng = store["store"]["coordinates"]["lon"]
        p = session.get(page, headers=headers, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        hours = soup.find("div", {"class": "storelocation__top__hours"}).findAll("li")
        for h in hours:
            h = h.text
            hoo = hoo + " " + h
            hoo = hoo
        hoo = hoo.replace("  ", " ")
        HOO = hoo
        hoo = ""

        data.append(
            [
                "https://www.dickblick.com/",
                page,
                storename,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
                HOO,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
