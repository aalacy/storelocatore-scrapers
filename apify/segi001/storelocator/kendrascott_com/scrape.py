import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8") as output_file:
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
    locator_domain = "https://www.kendrascott.com/"
    url = "https://www.kendrascott.com/stores/directory"
    missingString = "<MISSING>"

    s = sgrequests.SgRequests()

    stores = bs4.BeautifulSoup(s.get(url).text, features="lxml").findAll(
        "div", {"class": "search-item"}
    )

    result = []

    for store in stores:
        name = store.find("div", {"class": "store-name"}).text.strip().title()
        link = "{}{}".format(
            "https://www.kendrascott.com",
            store.find("a", {"class": "btn btn-link highlight-pin"})["href"],
        )
        addressJSON = {
            "address": store.find("p", {"class": "store-address"})
            .text.split("\n")[1]
            .title(),
            "city": store.find("p", {"class": "store-address"})
            .text.split("\n")[2]
            .title(),
            "state": store.find("p", {"class": "store-address"}).text.split("\n")[4],
            "zip": store.find("p", {"class": "store-address"}).text.split("\n")[5],
        }
        phone = store.find("a", {"class": "store-hours"}).text.strip()
        hours = (
            store.find("div", {"class": "store-hours"})
            .text.replace(
                "NOW OFFERING:LIMITED CAPACITY WALK-IN SHOPPING (MASK REQUIRED)BUY ONLINE, PICK UP CURBSIDEBUY ONLINE, PICK UP IN STOREHOURS (WEEK OF 12/28 - 1/4)",
                "",
            )
            .replace(
                "NOW OFFERING:LIMITED CAPACITY WALK-IN SHOPPING (MASK REQUIRED)BUY ONLINE, PICK UP CURBSIDEBUY ONLINE, PICK UP IN STOREHOURS (WEEK OF 12/28-1/4)",
                "",
            )
            .replace(
                "NOW OFFERING:LIMITED CAPACITY WALK-IN SHOPPING (MASK REQUIRED)BUY ONLINE, PICK UP CURBSIDEBUY ONLINE, PICK UP IN STOREHOURS (WEEK OF 12/28- 1/4)",
                "",
            )
            .replace(
                "NOW OFFERING:LIMITED CAPACITY WALK-IN SHOPPING (MASK REQUIRED)BUY ONLINE, PICK UP CURBSIDEBUY ONLINE, PICK UP IN STORESTORE & CAFÉ HOURS (WEEK OF 12/28 - 1/4)",
                "",
            )
            .replace(
                "View Our Sips & Sweets Café Menu",
                "",
            )
            .replace(
                "NOW OFFERING:LIMITED CAPACITY WALK-IN SHOPPING (MASK REQUIRED)BUY ONLINE, PICK UP CURBSIDEBUY ONLINE, PICK UP IN STORESTORE HOURS (WEEK OF 12/28 - 1/4)",
                "",
            )
            .replace("CLOSED", "Closed, ")
            .replace("MT", "M, T")
            .replace("MW", "M, W")
            .replace("MF", "M, F")
            .replace("MS", "M, S")
            .replace("MM", "M, M")
            .strip()
        )
        result.append(
            [
                locator_domain,
                link,
                name,
                addressJSON["address"],
                addressJSON["city"],
                addressJSON["state"],
                addressJSON["zip"],
                missingString,
                missingString,
                phone,
                missingString,
                store["data-storelat"],
                store["data-storelong"],
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
