import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("friospops_com")


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

    base_link = "https://friospops.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="entry-title")

    final_links = []
    for item in items:
        final_links.append(item.a["href"])

    data = []
    for final_link in final_links:
        logger.info(final_link)

        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "friospops.com"
        location_name = (
            "Frios Gourmet Pops - "
            + base.find_all(class_="elementor-text-editor elementor-clearfix")[0].text
        )

        try:
            raw_address = base.find_all(
                class_="elementor-text-editor elementor-clearfix"
            )[1].p.text.split("\n")
        except:
            raw_address = base.find_all(
                class_="elementor-text-editor elementor-clearfix"
            )[2].text

        if raw_address != "Historic Downtown McKinney":
            try:
                if "coming soon" in str(raw_address).lower():
                    continue
            except:
                continue
            try:
                street_address = raw_address[-3].strip() + " " + raw_address[-2].strip()
            except:
                try:
                    street_address = raw_address[-2].strip()
                except:
                    street_address = "<MISSING>"

            try:
                city_line = raw_address[-1].split(",")
            except:
                continue
            city = city_line[0].strip()
            if len(city) > 30:
                continue
            zip_code = city_line[-1][-6:].strip()
            if zip_code.isnumeric():
                state = city_line[1].split()[0].strip()
            else:
                try:
                    state = city_line[1].strip()
                    zip_code = "<MISSING>"
                except:
                    street_address = raw_address[0].strip()
                    city_line = raw_address[1].split(",")
                    city = city_line[0].strip()
                    state = city_line[1].split()[0].strip()
                    zip_code = city_line[-1][-6:].strip()
        else:
            street_address = "Historic Downtown"
            city = "McKinney"
            state = "TX"
            zip_code = "<MISSING>"

        if (
            "come to you" in street_address
            and "Charlotte, NC"
            in base.find_all(class_="elementor-text-editor elementor-clearfix")[
                1
            ].p.text
        ):
            street_address = "<MISSING>"
            city = "Charlotte"
            state = "NC"
            zip_code = "<MISSING>"
        if "fun van" in street_address.lower():
            street_address = "<MISSING>"

        if "569 1st St" in street_address:
            zip_code = "35007"

        street_address = street_address.replace(
            "TBD", "<MISSING>".replace("Frios Cart", "<MISSING>")
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find_all(class_="elementor-text-editor elementor-clearfix")[
            3
        ].text.strip()
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = (
            base.find_all(class_="elementor-text-editor elementor-clearfix")[5]
            .text.replace("*Poppy Hour", "")
            .replace("\n", " ")
            .strip()
        )
        if not hours_of_operation or "events" in hours_of_operation:
            hours_of_operation = "<MISSING>"

        hours_of_operation = hours_of_operation.replace("–", "-")

        if "purchase pops" in hours_of_operation.lower():
            hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        data.append(
            [
                locator_domain,
                final_link,
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
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
