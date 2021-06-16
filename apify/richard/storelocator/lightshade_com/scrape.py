import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lightshade_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():

    out = []
    locator_domain = "https://lightshade.com/"
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    url = "https://lightshade.com/wp-admin/admin-ajax.php"
    params = (
        ("action", "asl_load_stores"),
        ("nonce", "97453abb26"),
        ("load_all", "1"),
        ("layout", "1"),
    )
    r = session.get(url, headers=headers, params=params, verify=False)
    stores = r.json()

    for store in stores:
        link = store["website"]
        title = store["title"]
        sid = store["id"]
        ltype = "Store"
        street = store["street"]
        city = store["city"]
        pcode = store["postal_code"]
        state = store["state"]
        phone = store["phone"]
        lat = store["lat"]
        longt = store["lng"]
        hours = (
            "".join(store.get("open_hours"))
            .replace("[", "")
            .replace("]", "")
            .replace("}", "")
            .replace("{", "")
            .replace('"', "")
            .strip()
        )
        ccode = store["country"]
        if ccode == "United States":
            ccode = "US"

        row = [
            locator_domain,
            link,
            title,
            street,
            city,
            state,
            pcode,
            ccode,
            sid,
            phone,
            ltype,
            lat,
            longt,
            hours,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
