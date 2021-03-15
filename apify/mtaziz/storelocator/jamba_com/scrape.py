from sgrequests import SgRequests
import csv
import json
import time
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

logger = sglog.SgLogSetup().get_logger(logger_name="jamba_com")


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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        logger.info(f"No of records being processed: {len(temp_list)}")


session = SgRequests()
zips_radius100 = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)


def fetch_data():

    items = []
    locator_domainname = "jamba.com"
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }

    for zipcode in zips_radius100:
        url_test_api = (
            "https://www.jamba.com/sitecore/api/v1.0/jamba/storelocator/locations?locationname=%s"
            % (zipcode)
        )

        response = session.get(url_test_api, headers=headers)
        json_raw_data = response.text
        data_raw = json.loads(json_raw_data)
        data_raw = data_raw["Locations"]
        time.sleep(1)

        for store in data_raw:
            store_number = store["StoreNumber"] or "<MISSING>"
            locator_domain = locator_domainname
            page_url = store["Url"] or "<MISSING>"
            location_name = store["LocationName"] or "<MISSING>"
            street_address = store["StreetAddress"] or "<MISSING>"
            city = store["City"] or "<MISSING>"
            state = store["Region"] or "<MISSING>"
            zip = store["PostalCode"] or "<MISSING>"
            country_code = store["CountryName"] or "<MISSING>"
            store_number = store["StoreNumber"] or "<MISSING>"
            phone = store["Phone"] or "<MISSING>"
            location_type = store["LocationType"]["Name"] or "<MISSING>"
            latitude = store["Latitude"] or "<MISSING>"
            longitude = store["Longitude"] or "<MISSING>"
            hoo = store["Hours"]
            hoo = [
                "{} {} - {}".format(
                    hours_data["FormattedDayOfWeek"],
                    hours_data["Open"],
                    hours_data["Close"],
                )
                for hours_data in hoo
            ]
            hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"
            row = [
                locator_domain,
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
            items.append(row)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
