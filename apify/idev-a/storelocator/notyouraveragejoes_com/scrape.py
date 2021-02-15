import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

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
    base_url = "https://www.notyouraveragejoes.com"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": "_gcl_au=1.1.517320608.1612253406; _ga=GA1.2.1755591524.1612253407; _gid=GA1.2.775671990.1612253407",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }
    r = session.get("https://www.notyouraveragejoes.com/locations/", headers=headers)
    soup = bs(r.text, "lxml")
    links = soup.select("div.accordion-content a")

    data = []
    for link in links:
        locations_by_state_url = base_url + link["href"]
        r1 = session.get(locations_by_state_url, headers=headers)
        soup1 = bs(r1.text, "lxml")
        location_links = soup1.select("section.accordion-list[data-accordion='open'] a")
        for location_link in location_links:
            page_url = location_link["href"]
            r2 = session.get(page_url, headers=headers)
            soup2 = bs(r2.text, "lxml")
            location_name = soup2.select_one("h1.location__title span").string
            phone = soup2.select_one(
                "meta[property='restaurant:contact_info:phone_number']"
            )["content"]
            street_address = soup2.select_one(
                "meta[property='restaurant:contact_info:street_address']"
            )["content"]
            city = soup2.select_one(
                "meta[property='restaurant:contact_info:locality']"
            )["content"]
            zip = soup2.select_one(
                "meta[property='restaurant:contact_info:postal_code']"
            )["content"]
            state = soup2.select_one("meta[property='restaurant:contact_info:region']")[
                "content"
            ]
            country_code = soup2.select_one(
                "meta[property='restaurant:contact_info:country_name']"
            )["content"]
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = soup2.select_one("meta[property='place:location:latitude']")[
                "content"
            ]
            longitude = soup2.select_one("meta[property='place:location:longitude']")[
                "content"
            ]
            hours_of_operation = (
                soup2.select_one("span.location__hours").text[1:].strip().split("|")
            )
            if len(hours_of_operation) == 0:
                hours_of_operation = "Temporarily closed"
            else:
                hours_of_operation = ",".join(hours_of_operation)

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
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


if __name__ == "__main__":
    scrape()
