import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
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
    url = "https://physiciansimmediatecare.com/wp-admin/admin-ajax.php"
    p = 0
    loclist = session.post(
        url, data={"action": "get-nearby-clinics"}, headers=headers, verify=False
    ).json()
    for loc in loclist:
        store = loc["id"]
        title = loc["name"]
        phone = loc["phone"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zipcode"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        link = loc["url"]
        hourslist = loc["hours"]
        hours = ""
        for hr in hourslist:
            day = hr
            time = str(hourslist[hr])
            time = (
                time.replace("{", "")
                .replace("}", "")
                .replace(": ", " - ")
                .replace("'", "")
            )
            hours = hours + day + " " + time + " "
        data.append(
            [
                "https://physiciansimmediatecare.com/",
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
                hours,
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
