import csv
import sgrequests
import bs4


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
    # Your scraper here
    locator_domain = "https://www.landsend.com/"
    missingString = "<MISSING>"

    def getStoreMarkers():
        api = "https://www.landsend.com/pp/StoreLocator?lat=42.7456634&lng=-90.4879916&radius=200000&S=S&L=L&C=C&N=N"
        s = bs4.BeautifulSoup(
            sgrequests.SgRequests().get(api).text, features="lxml"
        ).findAll("marker")
        res = []
        for m in s:
            phone = m["phonenumber"]
            hours = m["storehours"]
            if not phone:
                phone = missingString
            if hours == "null":
                hours = missingString
            if "Germany" in m["state"]:
                pass
            elif "Japan" in m["state"]:
                pass
            elif "Rutland" in m["state"]:
                pass
            else:
                res.append(
                    {
                        "locator_domain": locator_domain,
                        "page_url": missingString,
                        "location_name": m["name"],
                        "street_address": m["address"],
                        "city": m["city"],
                        "state": m["state"],
                        "zip": m["zip"],
                        "country_code": missingString,
                        "store_number": m["storenumber"],
                        "phone": phone,
                        "location_type": m["storetype"],
                        "latitude": m["lat"],
                        "longitude": m["lng"],
                        "hours": hours,
                    }
                )
        return res

    result = []

    for s in getStoreMarkers():
        result.append(
            [
                s["locator_domain"],
                s["page_url"],
                s["location_name"],
                s["street_address"],
                s["city"],
                s["state"],
                s["zip"],
                s["country_code"],
                s["store_number"],
                s["phone"],
                s["location_type"],
                s["latitude"],
                s["longitude"],
                s["hours"],
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
