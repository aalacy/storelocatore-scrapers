import csv
import sgrequests
import json
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
    locator_domain = "https://uk.lush.com/"
    missingString = "<MISSING>"

    store_urls = []

    def retrieveStoreURLs(arr):
        for n in range(0, 13):
            req = json.loads(
                sgrequests.SgRequests()
                .get(
                    "https://uk.lush.com/ajax/get/{}/shops/100000/all/UK/ajax".format(n)
                )
                .text
            )
            s = bs4.BeautifulSoup(req[1]["data"], features="lxml")
            for a in s.findAll("a", href=True):
                if "shop" in a["href"]:
                    arr.append(a["href"])
        return set(arr)

    u = retrieveStoreURLs(store_urls)

    def initSoup(link):
        return bs4.BeautifulSoup(
            sgrequests.SgRequests().get(link).text, features="lxml"
        )

    def returnZIP(string):
        if len(string.split(" ")) == 2:
            return string
        if len(string.split(" ")) == 3:
            return string.split(" ")[-2] + " " + string.split(" ")[-1]
        if len(string.split(" ")) == 4:
            return string.split(" ")[-2] + " " + string.split(" ")[-1]
        if len(string.split(" ")) == 1:
            return missingString

    result = []

    for us in u:
        url = "{}{}".format(locator_domain, us.replace("/", "", 1))
        s = initSoup(url)
        if s.find("div", {"class": "object-hero-title"}) is None:
            pass
        else:
            name = s.find("div", {"class": "object-hero-title"}).text.strip()
            street = s.find(
                "div", {"class": "object-favourite-shop-address-line"}
            ).text.strip()
            zp = returnZIP(
                s.findAll("div", {"class": "object-favourite-shop-address-line"})[-1]
                .text.strip()
                .replace(name, "")
                .strip()
            )
            city = (
                s.findAll("div", {"class": "object-favourite-shop-address-line"})[-1]
                .text.strip()
                .replace(zp, "")
                .strip()
            )
            phone = (
                s.find("div", {"class": "shop-contact-details"})
                .text.strip()
                .split("\n")[1]
                .replace("Telephone: ", "")
            )
            # Retrieve store id
            store_num = (
                s.find("link", {"rel": "shortlink"})["href"]
                .replace("https://uk.lush.com/node/", "")
                .strip()
            )
            h = bs4.BeautifulSoup(
                sgrequests.SgRequests()
                .get("https://uk.lush.com/ajax/get/shoptimings/{}".format(store_num))
                .text,
                features="lxml",
            ).findAll("div", {"class": "opening-time"})
            timeArray = []
            for hs in h:
                day = hs.get_text(separator="\n").split("\n")[0]
                time = hs.get_text(separator="\n").split("\n")[1]
                timeArray.append(f"{day} : {time}")
            hours = ", ".join(timeArray)
            typ = missingString
            if hours == "":
                hours = missingString
                typ = "Closed"
            result.append(
                [
                    locator_domain,
                    url,
                    name,
                    street,
                    city,
                    missingString,
                    zp,
                    missingString,
                    store_num,
                    phone,
                    typ,
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
