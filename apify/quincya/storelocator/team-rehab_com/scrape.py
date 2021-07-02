import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://team-rehab.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1624488746023"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "team-rehab.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = base.find_all("item")

    for store in stores:
        link = "https://team-rehab.com" + store.exturl.text
        if "coming-soon" in link:
            continue
        if "autosave-v1" in link:
            continue
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find(class_="location__name").text
        try:
            street_address = (
                base.find(class_="col-sm-12 address__street").text
                + " "
                + base.find(class_="col-sm-12 address__street-2").text
            )
        except:
            street_address = base.find(class_="col-sm-12 address__street").text
        city_line = base.find(class_="col-sm-12 address__region").text.split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = base.find(id="phoneLocation").text
        latitude = store.latitude.text
        longitude = store.longitude.text
        location_type = "<MISSING>"

        hours_of_operation = ""
        try:
            hours_days = base.find(class_="hours__desktop").find_all(class_="long")
            hours_times = base.find(class_="hours__desktop").tbody.find_all("td")
            for i, row in enumerate(hours_days):
                day = hours_days[i].text
                hours = " ".join(list(hours_times[i].stripped_strings))
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours
                ).strip()
        except:
            hours_of_operation = "<MISSING>"

        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
