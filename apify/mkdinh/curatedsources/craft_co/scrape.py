import csv
from time import sleep
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("craft_co")
user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"

driver = SgSelenium().chrome(user_agent=user_agent)
driver.set_page_load_timeout(2 * 60 * 60)
driver.set_script_timeout(60)

fields = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(fields)
        for rows in data:
            writer.writerows(rows)


def get_fortune_100_companies():
    with open("fortune_100.csv") as file:
        reader = csv.reader(file, delimiter=",")
        header = next(reader)
        return [record for record in reader]


def fetch_company(slug):
    # bypassing same origin constraints
    query = driver.execute_async_script(
        f"""
            var done = arguments[0];
            fetch("https://craft.co/proxy/dodo/query", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{
                "operationName": "getCompany",
                "variables":{{
                        "slug":"{slug}"
                    }}  
                }})
            }})
            .then(res => res.json())
            .then(done);
        """
    )

    return query.get("data").get("company")


def resolve_country_code(country):
    if country == "United States":
        return "US"
    elif country == "Canada":
        return "CA"
    else:
        return None


def get_country_code(location, company):
    country = location.get("country")
    locations = company.get("locationsWithCityCountryAddress")
    loc = next((loc for loc in locations if loc.get("id") == location.get("id")), None)

    if not loc:
        return resolve_country_code(country)

    return loc.get("countryCode") or resolve_country_code(country)


def fetch_company_locations(company):
    slug = company.get("slug")
    hq_id = company.get("hqLocation").get("id")
    # bypassing same origin constraints
    query = driver.execute_async_script(
        f"""
        var done = arguments[0];
        fetch("https://craft.co/proxy/dodo/query", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify({{
              "operationName": "getCompanyLocations",
              "variables":{{
                    "countryCodes":["CA", "US"],
                    "page":1,
                    "per":1000,   
                    "slug":"{slug}"
                  }}  
            }})
        }})
        .then(res => res.json())
        .then(done);
        """
    )

    locations = query.get("data").get("company").get("locationsPage").get("locations")

    for location in locations:
        location["countryCode"] = get_country_code(location, company)

    return locations


MISSING = "<MISSING>"


def get(location, key):
    return location.get(key, MISSING) or MISSING


def extract(company, location, name):
    slug = company.get("slug")
    record = {
        "locator_domain": "craft.co",
        "page_url": f"https://craft.co/{slug}",
        "street_address": get(location, "address").replace("\r\n", " "),
        "city": get(location, "city"),
        "state": get(location, "state"),
        "zip": get(location, "zipCode"),
        "country_code": get(location, "countryCode"),
        "latitude": get(location, "latitude"),
        "longitude": get(location, "longitude"),
        "location_type": "HQ" if location.get("hq") else "Office",
        "location_name": name,
        "store_number": location.get("id"),
        "phone": MISSING,
        "hours_of_operation": MISSING,
    }

    return [record[field] for field in fields]


def fetch_locations(slug, name):
    try:
        company = fetch_company(slug)
        locations = fetch_company_locations(company)
        return [extract(company, location, name) for location in locations]
    except Exception as ex:
        logger.info(f"retrying: {slug}")
        return fetch_locations(slug, name)


def fetch_data():
    driver.get(f"https://craft.co")
    failed = []
    fortune_100_companies = get_fortune_100_companies()
    slugs = [company[0] for company in fortune_100_companies]

    for slug, url, name, rank in fortune_100_companies:
        yield fetch_locations(slug, name)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
