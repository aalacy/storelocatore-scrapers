from sgselenium import SgChrome
import csv


def fetch_data():
    locator_domain = "akisushi.ca"
    url = "https://akisushi.ca/nos-succursales/?lat=46.8157795&long=-71.21788149999999"
    with SgChrome() as driver:
        driver.get(url)
        locations = driver.execute_script("return locations")

    output = []
    for row in locations:
        currentrow = []
        currentrow.append(locator_domain)
        currentrow.append(url)
        currentrow.append(row[0])
        currentrow.append(row[4])
        currentrow.append(row[5])
        currentrow.append(row[6])
        currentrow.append(row[7])
        currentrow.append("CA")
        currentrow.append("<MISSING>")
        currentrow.append(row[8])
        currentrow.append(row[9])
        currentrow.append(row[1])
        currentrow.append(row[2])
        currentrow.append(row[11])
        currentrow = ["<MISSING>" if point is None else point for point in currentrow]
        output.append(currentrow)
    return output


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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
