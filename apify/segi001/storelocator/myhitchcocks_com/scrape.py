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
    locator_domain = "https://www.myhitchcocks.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    s = initSoup("https://www.myhitchcocks.com/locations/")

    result = []

    for e in s.findAll(
        "div", {"class": "store-list-row-container store-bucket filter-rows"}
    ):
        name = e.find("a", {"class": "store-name"}).text.strip()
        city = name
        state = e.find("a", {"class": "store-name"})["data-state"]
        street = (
            e.find("div", {"class": "store-address"})
            .get_text(separator="\n")
            .split("\n")[0]
        )
        zp = "".join(
            filter(
                str.isdigit,
                e.find("div", {"class": "store-address"})
                .get_text(separator="\n")
                .split("\n")[1]
                .replace(",", "")
                .replace(state, "")
                .replace(city, "")
                .strip(),
            )
        )
        phone = (
            e.find("a", {"class": "store-phone"})
            .text.strip()
            .replace("(", "")
            .replace(")", "")
        )
        hours = (
            e.find("div", {"class": "store-list-row-item-col02"})
            .text.strip()
            .replace("\r\n", "")
        )
        lat = (
            e.findAll("a", href=True)[-1]["href"]
            .replace("https://www.google.com/maps/dir/Current+Location/", "")
            .split(",")[0]
            .strip()
        )
        lng = (
            e.findAll("a", href=True)[-1]["href"]
            .replace("https://www.google.com/maps/dir/Current+Location/", "")
            .split(",")[1]
            .strip()
        )
        result.append(
            [
                locator_domain,
                missingString,
                name,
                street,
                city,
                state,
                zp,
                missingString,
                missingString,
                phone,
                missingString,
                lat,
                lng,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
