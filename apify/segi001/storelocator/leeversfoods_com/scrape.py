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
    locator_domain = "https://www.leeversfoods.com/"
    missingString = "<MISSING>"

    def req(l):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        return sgrequests.SgRequests().get(l, headers=headers)

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    def getStores():
        s = initSoup("https://www.leeversfoods.com/store-locations/")
        res = []
        for ss in s.findAll("a", href=True):
            if "/store-locations/" in ss["href"]:
                if ss["href"] == "https://www.leeversfoods.com/store-locations/":
                    pass
                else:
                    res.append(ss["href"])
        return list(set(res))

    stores = getStores()

    result = []

    for store in stores:
        s = initSoup(store)
        name = (
            s.find("h2", {"itemprop": "headline"})
            .text.strip()
            .replace("Leevers", "")
            .replace("Liquor Locker", "")
        )
        street = (
            s.find("div", {"itemprop": "text"})
            .get_text(separator="\n")
            .strip()
            .split("\n")[0]
            .strip()
        )
        city = (
            s.find("div", {"itemprop": "text"})
            .get_text(separator="\n")
            .strip()
            .split("\n")[2]
            .strip()
            .split(",")[0]
            .strip()
        )
        state = (
            s.find("div", {"itemprop": "text"})
            .get_text(separator="\n")
            .strip()
            .split("\n")[2]
            .strip()
            .split(",")[1]
            .strip()
            .split(" ")[0]
            .strip()
        )
        zp = list(
            filter(
                None,
                s.find("div", {"itemprop": "text"})
                .get_text(separator="\n")
                .strip()
                .split("\n")[2]
                .strip()
                .split(",")[1]
                .strip()
                .replace("\xa0", " ")
                .split(" "),
            )
        )[1].strip()
        phone = (
            s.findAll("div", {"itemprop": "text"})[1]
            .text.strip()
            .replace("Phone:", "")
            .strip()
        )
        hours = (
            s.findAll("div", {"itemprop": "text"})[3]
            .text.strip()
            .replace("Hours:", "")
            .strip()
        )
        if hours == "":
            hours = (
                s.findAll("div", {"itemprop": "text"})[4]
                .text.strip()
                .replace("Hours:", "")
                .strip()
            )
        result.append(
            [
                locator_domain,
                store,
                name,
                street,
                city,
                state,
                zp,
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
