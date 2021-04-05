import csv
from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome, ChromeOptions


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


# encounter CloudFlare captcha due to sslProxy issue with seleniumwire
# workaround until a solution is found
def get_driver():
    options = ChromeOptions()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    )

    return Chrome(options=options, executable_path="/bin/chromedriver")


def fetch_data():
    store_link = "https://www.northerntool.com/stores"
    base_link = "https://www.northerntool.com/stores/stores.xml"

    driver = get_driver()
    driver.get(store_link)
    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "html.parser")
    store_data = base.find_all("row")

    data = []
    locator_domain = "northerntool.com"

    for store in store_data:
        location_name = store.h1.text
        street_address = store.address.text.replace("<br>", " ").strip()
        city = store.city.text.strip()
        state = store.state.text.strip()
        zip_code = store.zipcode.text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store.phone.text.strip()
        hours_of_operation = store.storehours.text.replace("<br/>", " ")
        latitude = store.coordinates.text.split(",")[0].strip()
        longitude = store.coordinates.text.split(",")[1].strip()
        link = "https://www.northerntool.com/stores/" + store.url.text

        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
