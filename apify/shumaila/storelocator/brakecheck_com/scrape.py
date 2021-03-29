import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    data = []
    addr = [
        "lat=29.5330493&lng=-98.78116449999999",
        "lat=30.2228447&lng=-97.74735720000001",
        "lat=27.700785&lng=-97.3462545",
        "lat=28.80663839999999&lng=-96.99609249999999",
    ]
    for latnow in addr:

        base_url = (
            "https://brakecheck.com/wp-content/plugins/store-locator/content/phpsqlsearch_genxml.php?"
            + latnow
            + "&radius=100&alignment=undefined&brakecheck=undefined&oilchange=undefined"
        )
        r = session.get(base_url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        data_list = soup.findAll("marker")
        for loc in data_list:
            title = loc["name"]
            street = loc["address"]
            lat = loc["lat"]
            lng = loc["lng"]
            phone = loc["phone"]
            city = loc["city"]
            state = loc["state"]
            zip = loc["zip"]
            pageurl = "https://brakecheck.com/" + loc["url"]
            storenum = loc["store_no"]
            hours_of_operation = (
                loc["weekday_hours"]
                .replace("<b>", "")
                .replace("</b>", "")
                .replace("\n", " ")
                + ", "
                + loc["sunday_hours"]
            )
            if "San Antonio Store 438" in title:
                hours_of_operation = "Mon - Sat: 7:30am - 6pm, Sun: 9am - 5pm"
            data.append(
                [
                    "www.brakecheck.com",
                    pageurl,
                    title,
                    street,
                    city,
                    state,
                    zip,
                    "US",
                    storenum,
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
                    hours_of_operation,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
