import csv
from time import sleep
from sgselenium import SgSelenium

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
        for row in data:
            writer.writerow(row)


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


def fetch_hq(company):
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
                    "countryCodes":[],
                    "page":1,
                    "per":32,
                    "slug":"{slug}"
                  }}  
            }})
        }})
        .then(res => res.json())
        .then(done);
        """
    )

    locations = query.get("data").get("company").get("locationsPage").get("locations")
    hq = next(location for location in locations if location.get("id") == hq_id)
    hq_location = next(
        (
            location
            for location in company.get("locationsWithCityCountryAddress")
            if location.get("id") == hq_id
        )
    )
    hq["countryCode"] = hq_location["countryCode"]

    return hq


MISSING = "<MISSING>"


def extract(company, hq, name):
    slug = company.get("slug")
    return {
        "locator_domain": "craft.co",
        "page_url": f"https://craft.co/{slug}",
        "street_address": hq.get("address", MISSING).replace("\r\n", " "),
        "city": hq.get("city", MISSING),
        "state": hq.get("state", MISSING),
        "zip": MISSING,
        "country_code": hq.get("countryCode", MISSING),
        "latitude": hq.get("latitude"),
        "longitude": hq.get("longitude"),
        "location_type": "HQ",
        "location_name": name,
        "store_number": company.get("id", MISSING),
        "phone": MISSING,
        "hours_of_operation": MISSING,
    }


def fetch_location(slug, name):
    try:
        company = fetch_company(slug)
        hq = fetch_hq(company)
        location = extract(company, hq, name)
        return location
    except:
        return fetch_location(slug)


def fetch_data():
    driver.get(f"https://craft.co")
    failed = []
    fortune_100_companies = get_fortune_100_companies()
    slugs = [company[0] for company in fortune_100_companies]

    for slug, url, name, rank in fortune_100_companies:
        try:
            location = fetch_location(slug, name)
            yield [location.get(field, MISSING) for field in fields]
        except Exception as ex:
            failed.append(slug)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
