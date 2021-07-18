from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    url = "https://oilchangers.com/wp-admin/admin-ajax.php"
    p = 0
    loclist = session.post(
        url, headers=headers, data={"action": "get_all_stores"}, verify=False
    ).json()
    for loc in loclist:
        loc = loclist[loc]
        store = loc["ID"]
        title = loc["na"]
        link = loc["gu"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["st"]
        city = loc["ct"]
        state = loc["rg"]
        pcode = loc["zp"]
        phone = loc["te"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("div", {"class": "store_locator_single_opening_hours"})
            .text.replace("Opening Hours ", "")
            .strip()
        )

        hours = hours.encode("ascii", "ignore").decode("ascii")
        phone = phone.encode("ascii", "ignore").decode("ascii")
        street = street.encode("ascii", "ignore").decode("ascii")
        city = city.encode("ascii", "ignore").decode("ascii")
        state = state.encode("ascii", "ignore").decode("ascii")
        pcode = pcode.encode("ascii", "ignore").decode("ascii")
        title = title.encode("ascii", "ignore").decode("ascii")
        data.append(
            [
                "https://oilchangers.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours.replace("\n", " ").lstrip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
