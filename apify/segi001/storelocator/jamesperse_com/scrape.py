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
    locator_domain = "https://www.jamesperse.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def s(l):
        r = req(l)
        return [r, bs4.BeautifulSoup(r.text, features="lxml")]

    def sortStores():
        locations = {"UK": "boutique-GB", "CA": "boutique-CA", "US": "boutique-US"}
        b = s("https://www.jamesperse.com/stores/boutique")
        bo = b[1].findAll("div", {"class": "boutique-group"})
        r = []
        for e in bo:
            if locations["UK"] in e["class"][0]:
                r.append(e)
            if locations["CA"] in e["class"][0]:
                r.append(e)
            if locations["US"] in e["class"][0]:
                r.append(e)
        return r

    # Sorting HTML elements by US,UK and CA
    storeObjects = sortStores()

    def addressParser(a):
        addr = list(filter(None, a.split(" ")))
        if len(addr) == 3:
            return {
                "city": addr[0],
                "state": addr[1],
                "zip": addr[2],
                "country": missingString,
            }
        if len(addr) == 4:
            return {
                "city": addr[0] + " " + addr[1],
                "state": addr[2],
                "zip": addr[3],
                "country": missingString,
            }
        if len(addr) == 5:
            return {
                "city": addr[0],
                "state": addr[1],
                "country": addr[2],
                "zip": addr[3] + " " + addr[4],
            }

    result = []

    for obj in storeObjects:
        name = obj["location"]
        addr = list(
            filter(None, obj.find("p").text.replace("Map", "").strip().split("\n"))
        )
        street = addr[0].strip()
        city = addressParser(addr[-1].strip())
        phone = (
            obj.findAll("p")[1]
            .text.replace("Tel", "")
            .replace(obj.find("a").text, "")
            .strip()
            .split("\n")[0]
            .strip()
            .split("  ")[0]
        )
        if len(obj.findAll("p")) == 3:
            hours = list(
                filter(
                    None,
                    obj.findAll("p")[2]
                    .text.replace("Store Hours:", "")
                    .strip()
                    .split("\n"),
                )
            )
        else:
            pass
        h = []
        for ho in hours:
            if "ONLINE ONLY | NO WALK-INS" in ho:
                h.append(missingString)
            else:
                h.append(ho.replace(u"\r", ""))
        hou = ", ".join(h)
        result.append(
            [
                locator_domain,
                missingString,
                name,
                street,
                city["city"],
                city["state"],
                city["zip"],
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hou,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
