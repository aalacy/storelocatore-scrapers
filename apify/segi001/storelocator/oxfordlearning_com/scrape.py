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
    locator_domain = "https://www.oxfordlearning.com/"
    missingString = "<MISSING>"

    def allLocations():
        sess = sgrequests.SgRequests()
        h = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
        }
        res = []
        bs = bs4.BeautifulSoup(
            sess.get(
                "https://gradepowerlearning.com/locations/#location-filter-postal",
                headers=h,
            ).text,
            features="lxml",
        )
        lnks = bs.findAll("a", {"class": "location-item-link button tertiary small"})
        for l in lnks:
            b = bs4.BeautifulSoup(sess.get(l["href"], headers=h).text, features="lxml")
            name = (
                b.find("h1", {"itemprop": "name"}).text.strip().replace("Tutoring", "")
            )
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
            phone = (
                b.find("address", {"itemprop": "address"})
                .find_next("p")
                .find("a")["href"]
                .replace("tel:", "")
            )
            if phone == "":
                phone = missingString
            res.append(
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
        return res

    result = allLocations()
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
