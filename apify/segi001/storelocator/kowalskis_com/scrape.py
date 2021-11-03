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
    locator_domain = "https://www.kowalskis.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initS(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    def retreiveStores():
        s = initS("https://www.kowalskis.com/sitemap.xml")
        res = []
        for loc in s.findAll("loc"):
            if "/location/" in loc.text:
                res.append(loc.text)
        return res

    stores = retreiveStores()

    result = []

    for store in stores:
        s = initS(store)
        name = s.find("span", {"class": "title"}).text.strip()
        street = s.find("span", {"class": "address-line1"}).text.strip()
        url = store
        city = s.find("span", {"class": "locality"}).text.strip()
        state = s.find("span", {"class": "administrative-area"}).text.strip()
        zp = s.find("span", {"class": "postal-code"}).text.strip()
        code = s.find("span", {"class": "country"}).text.strip()
        phone = missingString
        if not s.find("div", {"class": "field phone label-inline"}):
            phone = missingString
        else:
            phone = (
                s.find("div", {"class": "field phone label-inline"})
                .find("a")
                .text.strip()
            )
        tA = []
        if not s.findAll("div", {"class": "field-content"})[-1]:
            pass
        else:
            h = list(
                filter(
                    None,
                    s.findAll("div", {"class": "field-content"})[-1]
                    .find("p")
                    .get_text(separator="\n")
                    .split("\n"),
                )
            )
            if "United States" in h[-1]:
                tA.append(missingString)
            else:
                h.pop(0)
                if len(h) == 1:
                    tA.append(h[0])
                else:
                    tA.append(h[0])
                    tA.append(h[1])
        hour = ", ".join(tA)
        result.append(
            [
                locator_domain,
                url,
                name,
                street,
                city,
                state,
                zp,
                code,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hour,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
