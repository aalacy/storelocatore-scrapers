import csv
import re
from lxml import html
from sgrequests import SgRequests


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
    locator_domain = "http://marvalfoodstores.org"
    page_url = "http://marvalfoodstores.org/locations_new.php"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath("//map[@name='Map']/area")

    for d in div:
        add = "".join(d.xpath(".//@href"))
        addres = add.split("place/")[1].split("/")[0]

        location_name = addres.split(",")[1].replace("+", " ").strip()
        street_address = addres.split(",")[0].replace("+", " ")
        ad = addres.split(",")[2].replace("+", " ").strip()
        city = addres.split(",")[1].replace("+", " ").strip()
        state = ad.split()[0].strip()
        country_code = "US"
        postal = ad.split()[1].strip()
        store_number = "<MISSING>"
        try:
            if add.find("ll=") != -1:
                latitude = add.split("ll=")[1].split(",")[0]
                longitude = add.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = add.split("@")[1].split(",")[0]
                longitude = add.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        phone = "<INACCESSIBLE >"
        session = SgRequests()
        r = session.get("https://marvalfoodstores.org/")
        tree = html.fromstring(r.text)
        text = (
            "".join(tree.xpath("//h6/text()"))
            .replace("Mon", "mon")
            .replace("Sat", "sat")
            .replace("Sun", "sun")
            .replace("Springs", "springs")
        )
        res_list = [s for s in re.split("([A-Z][^A-Z]*)", text) if s]
        res_list = (
            ";".join(res_list)
            .replace(
                "Willows mon -  sun 7 am - 9 pm", "Willows mon -  sun 7 am - 9 pm;"
            )
            .replace("Valley springs", "Valley Springs")
        )
        hours_of_operation = (
            res_list.split(city)[1]
            .split(";")[0]
            .replace("mon", "Mon")
            .replace("sat", "Sat")
            .replace("sun", "Sun")
            .strip()
        )

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
