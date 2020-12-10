from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
import csv


logger = SgLogSetup().get_logger("bubbas33_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "www.bubbas33.com",
    "method": "GET",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_gcl_au=1.1.183413411.1606154150; _ga=GA1.2.1142113799.1606154151; _fbp=fb.1.1606154151724.735650847; _gid=GA1.2.1092831572.1606324472; _gat_UA-67993700-1=1",
    "referer": "https://www.bubbas33.com/locations",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
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
    timings = ""
    opentime = ""
    closetime = ""
    url = "https://www.bubbas33.com/api/locations"
    r = session.get(url, headers=headers, verify=False).json()
    for loc in r:
        street = loc["address1"]
        city = loc["city"]
        state = loc["state"]
        postalCode = loc["postalCode"]
        telephone = loc["telephone"]
        latitude = loc["latitude"]
        longitude = loc["longitude"]
        url = loc["onlineToGoUrl"]
        title = loc["name"]
        schedule = loc["schedule"]
        # print(schedule)
        for ti in schedule:
            day = ti["day"]
            hours = ti["hours"]
            opentime = hours["openTime"]
            closetime = hours["closeTime"]
            timings = timings + day + ": " + opentime + "-" + closetime + " "
        sched = timings
        timings = ""

        data.append(
            [
                "https://www.bubbas33.com/",
                "https://www.bubbas33.com/locations",
                title,
                street,
                city,
                state,
                postalCode,
                "US",
                "<MISSING>",
                telephone,
                "<MISSING>",
                latitude,
                longitude,
                sched,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
