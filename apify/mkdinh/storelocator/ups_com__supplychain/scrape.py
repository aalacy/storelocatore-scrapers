import re
import csv
from sglogging import SgLogSetup
from urllib.request import Request, urlopen
import tabula as tb  # noqa
from io import BytesIO

logger = SgLogSetup().get_logger("ups_com__supplychain")
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

MISSING = "<MISSING>"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(fields)
        # Body
        for row in data:
            writer.writerow(row)


def read_pdf_to_dataframes(url):
    table_column_boundaries = [54, 197, 339, 658]
    with urlopen(Request(url)) as file:
        memoryFile = BytesIO(file.read())
        dataframes = tb.read_pdf(
            memoryFile, pages="all", columns=table_column_boundaries
        )
        return dataframes


def is_beginning_data_row(row):
    return is_string(row["Country"]) or is_string(row["City"])


def is_string(value):
    return isinstance(value, str)


def get_phone(contact):
    for item in contact:
        if "Phone" in item:
            phone = re.split(r"[\/|;]", item)[0]
            return re.sub(r"[\D|\s]", "", phone)
            break


def get_locations_from_dataframes(dataframes):
    locations = []
    row_data = {}
    for df in dataframes:
        if "Country" in df:
            for i, row in df.iterrows():
                contact = row["Contact"]

                if is_beginning_data_row(row):
                    country = row["Country"]
                    city = row["City"]

                    if i:
                        previous_row = df.loc[i - 1, :]
                        if is_beginning_data_row(previous_row):
                            row_data["country"] += (
                                f" {country}" if is_string(country) else ""
                            )
                            row_data["city"] += f" {city}" if is_string(city) else ""
                            row_data["contact"].append(contact)
                            continue

                        locations.append(row_data)

                    row_data = {}
                    row_data["country"] = country

                    row_data["city"] = city
                    row_data["contact"] = []

                row_data["contact"].append(contact)

                if i == len(df) - 1:
                    locations.append(row_data)
                    row_data = {}

    return locations


def get_zip(contact):
    canada_zip = "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]"
    us_zip = "[0-9]{5}"
    us_extended_zip = "[0-9]{5}-[0-9]{4}"
    zip_regexp = f"({canada_zip}|{us_extended_zip}|{us_zip})"

    for item in contact:
        match = re.search(zip_regexp, item)
        if match:
            return match.group(0)

    return MISSING


def get_country_code(country):
    if country == "United States":
        return "US"

    elif country == "Canada":
        return "CA"
    else:
        return MISSING


def extract(location):
    poi = {}
    contact = location["contact"]

    poi["locator_domain"] = "ups.com"
    poi["location_name"] = contact[0]

    poi["phone"] = get_phone(contact)

    state, country = re.split(", ", location["country"])

    poi["city"] = location["city"].split(", ")[0]

    street_address = contact[1].strip()
    poi["street_address"] = re.sub(poi["city"], "", street_address, re.I).strip()

    poi["state"] = state
    poi["country_code"] = get_country_code(country)
    poi["zip"] = get_zip(contact)

    poi["page_url"] = MISSING
    poi["latitude"] = MISSING
    poi["longitude"] = MISSING
    poi["hours_of_operation"] = MISSING
    poi["location_type"] = MISSING
    poi["store_number"] = MISSING

    return poi


def filter_only_us_canada_locations(locations):
    return [
        location
        for location in locations
        if re.search("United States|Canada", location["country"])
    ]


def fetch_data():
    url = "https://www.ups.com/assets/resources/supplychain/media/global-locations-directory.pdf"
    dataframes = read_pdf_to_dataframes(url)
    locations = get_locations_from_dataframes(dataframes)
    us_canada_locations = filter_only_us_canada_locations(locations)

    for location in us_canada_locations:
        poi = extract(location)
        yield [poi[field] for field in fields]


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
