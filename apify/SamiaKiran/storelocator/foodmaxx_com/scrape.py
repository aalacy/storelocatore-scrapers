import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("foodmaxx_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrf-token": "bcn1ZNhK5xJjZ-8kpgjEhgk_075f7gNn-ZuapxG5Rxg",
    "cookie": "__cfduid=dd5846943fc34219468250754e96c18711605080230; _ga=GA1.2.566923491.1605080241; _gid=GA1.2.481180814.1605080241; SESS99fe6f1d7a6e8ceefcd0898a29c1d5de=6oWkHYdVfKbT_ICCGga7EnEM0Ak9KVpUAn1G9Rfv6lk; __zlcmid=117jZph3a0gx0E8; preservedStoreIDFromLogout=6672; SSESS99fe6f1d7a6e8ceefcd0898a29c1d5de=eYPxyBhyuZtZZ4uIBkMwth6i1EuexGHk84gR5PT2DeE; XSRF-TOKEN=bcn1ZNhK5xJjZ-8kpgjEhgk_075f7gNn-ZuapxG5Rxg; has_js=1; session=1605286799527.vzahqf9t; _gat_UA-132993060-1=1; _gat_UA-102256819-3=1",
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
    # Your scraper here
    data = []
    url = "https://www.foodmaxx.com/api/m_store_location?store_type_ids=1,2,3"
    loclist = session.get(url, headers=headers, verify=False).json()["stores"]
    print(loclist)
    daylist = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    for loc in loclist:
        title = loc["storeName"]
        store = loc["store_number"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        ccode = loc["country"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        phone = loc["phone"]
        hour_list = loc["store_hours"]
        hours = ""
        for hr in hour_list:
            day = daylist[hr["day"]]
            start = hr["open"]
            close = hr["close"]
            hours = hours + day + " " + start + " - " + close + " "
        data.append(
            [
                "https://www.foodmaxx.com/",
                "https://www.foodmaxx.com/stores",
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
