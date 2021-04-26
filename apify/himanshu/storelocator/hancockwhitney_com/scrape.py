import csv
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hancockwhitney_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
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


def fetch_data():

    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)
    for lat, lng in coords:
        logger.info(f"Pulling records for {lat,lng}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
        r = session.get(
            "https://hancockwhitney-api-production.herokuapp.com/location?latitude="
            + lat
            + "&locationTypes=atm,branch,business&longitude="
            + lng
            + "&pageSize=100&radius=50&searchByState=&sort=distance&sortDir=-1",
            headers=headers,
        )
        data = r.json()["data"]
        for store_data in data:
            store = []
            store.append("https://www.hancockwhitney.com")
            store.append(store_data["name"])
            store.append(store_data["address"]["street"])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zip"])
            store.append("US")
            store.append("<MISSING>")
            store.append(
                store_data["phone"].replace("_", "-")
                if "phone" in store_data
                and store_data["phone"]
                and store_data["phone"] != "TBD"
                else "<MISSING>"
            )
            store.append(", ".join(store_data["locationTypes"]))
            store.append(str(store_data["geo"]["coordinates"][1]))
            store.append(str(store_data["geo"]["coordinates"][0]))
            hours = ""
            if "lobbyHours" in store_data:
                hours = store_data["lobbyHours"]

            if len(hours) <= 0:
                if "atmHours" in store_data:
                    hours = store_data["atmHours"]

            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
