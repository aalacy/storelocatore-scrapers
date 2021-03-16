import csv
import sgrequests
import bs4
import re


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
        country = missingString
        if len(addr) == 3:
            return {
                "city": addr[0],
                "state": addr[1],
                "zip": addr[2],
                "country": country,
            }
        if len(addr) == 4:
            return {
                "city": addr[0] + " " + addr[1],
                "state": addr[2],
                "zip": addr[3],
                "country": country,
            }
        if len(addr) == 5:
            return {
                "city": addr[0],
                "state": addr[1],
                "country": "United Kingdom",
                "zip": addr[3] + " " + addr[4],
            }

    result = []

    for obj in storeObjects:
        name = obj["location"]
        addr = list(
            filter(None, obj.find("p").text.replace("Map", "").strip().split("\n"))
        )
        if "ONLINE ORDERS ONLY" in addr[0].strip() or "James Perse" in addr[0].strip():
            street = addr[1].strip()
        else:
            street = addr[0].strip()
        city = addressParser(addr[-1].strip())
        c = city["country"]
        if "Canada" in " ".join(addr):
            c = "Canada"
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
            if "ONLINE ORDERS ONLY | NO WALK-INS" in ho:
                h.append(missingString)
            else:
                h.append(ho.replace(u"\r", ""))
        hou = ", ".join(h)
        lat = missingString
        lng = missingString
        if not obj.find("a", {"target": "_blank"}):
            pass
        else:
            latlng = re.search(r"@(.*?)/", obj.find("a", {"target": "_blank"})["href"])
            if latlng:
                grouped = list(
                    filter(
                        None,
                        latlng.group(1)
                        .replace("17z", "")
                        .replace("@", "")
                        .replace("3a,90y,318.67h,82.51t", "")
                        .split(","),
                    )
                )
                lat = grouped[0]
                lng = grouped[1]
        result.append(
            [
                locator_domain,
                missingString,
                name,
                street,
                city["city"],
                city["state"],
                city["zip"],
                c,
                missingString,
                phone,
                missingString,
                lat,
                lng,
                hou,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
