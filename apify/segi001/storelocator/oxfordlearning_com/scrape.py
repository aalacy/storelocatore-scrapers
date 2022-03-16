import csv
import sgrequests
import bs4
import ast


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
    locator_domain = "https://www.oxfordlearning.com/"
    missingString = "<MISSING>"
    r = []
    sess = sgrequests.SgRequests()

    h = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }

    def allLocations(lnk):
        bs = bs4.BeautifulSoup(
            sess.get(
                lnk,
                headers=h,
            ).text,
            features="lxml",
        )
        lnks = bs.findAll("a", {"class": "location-item-link button tertiary small"})
        for l in lnks:
            r.append(l)

    allLocations("https://gradepowerlearning.com/locations/#location-filter-postal")
    allLocations("https://www.oxfordlearning.com/locations/?fprov=313&fpostal=")

    result = []
    for l in r:
        b = bs4.BeautifulSoup(sess.get(l["href"], headers=h).text, features="lxml")
        if b.find("h1", {"itemprop": "name"}):
            name = (
                b.find("h1", {"itemprop": "name"}).text.strip().replace("Tutoring", "")
            )
        else:
            name = missingString
        url = l["href"]
        if b.find("span", {"itemprop": "streetAddress"}) is None:
            street = missingString
        else:
            street = b.find("span", {"itemprop": "streetAddress"}).text.strip()
        if b.find("span", {"itemprop": "addressLocality"}) is None:
            city = missingString
        else:
            city = b.find("span", {"itemprop": "addressLocality"}).text.strip()
        if b.find("span", {"itemprop": "addressRegion"}) is None:
            state = missingString
        else:
            state = b.find("span", {"itemprop": "addressRegion"}).text.strip()
        if b.find("span", {"itemprop": "postalCode"}) is None:
            zp = missingString
        else:
            zp = b.find("span", {"itemprop": "postalCode"}).text.strip()
        timeArray = []
        for hs in b.findAll("div", {"class": "dl-item clearfix"}):
            hr = list(filter(None, hs.get_text(separator="\n").strip().split("\n")))
            hr_str = " ".join(hr)
            timeArray.append(hr_str)
        hours = ", ".join(timeArray)
        if hours == "":
            hours = missingString
        if zp == "":
            zp = missingString
        if b.find("address", {"itemprop": "address"}):
            phone = (
                b.find("address", {"itemprop": "address"})
                .find_next("p")
                .find("a")["href"]
                .replace("tel:", "")
            )
        else:
            phone = missingString
        if phone == "":
            phone = missingString
        result.append(
            [
                locator_domain,
                url,
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

    resu = []

    for e in result:
        resu.append(str(e))

    results = []

    for el in set(resu):
        results.append(ast.literal_eval(el))

    return results


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
