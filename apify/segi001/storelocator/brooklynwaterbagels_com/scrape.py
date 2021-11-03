import req
import bs4
import csv


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
    locator_domain = "https://www.brooklynwaterbagel.com/"
    missingString = "<MISSING>"

    def send(l):
        return req.Req().get(l)

    def initSoup(l):
        return bs4.BeautifulSoup(send(l).text, features="lxml")

    def getAllStores():
        s = initSoup("https://www.brooklynwaterbagel.com/locations/")
        r = []
        for e in s.findAll("article", {"class": "column single__location"}):
            url = e.find("h3").find("a")["href"]
            r.append(url)
        return r

    s = getAllStores()

    def parseAddress(a):
        spl = a.split(",")
        street = missingString
        zp = missingString
        city = missingString
        state = missingString
        if "Ste" in spl[1] or "Unit" in spl[1]:
            street = spl[0] + " " + spl[1]
            city = spl[2]
        if len(spl[2].strip().split(" ")) == 1:
            if "Ste" in spl[1] or "Unit" in spl[1]:
                street = spl[0] + " " + spl[1]
                city = spl[2]
            else:
                street = spl[0]
                city = spl[1]
                state = spl[2]
        else:
            if "Ste" in spl[1] or "Unit" in spl[1]:
                street = spl[0] + " " + spl[1]
                city = spl[2]
            else:
                street = spl[0]
                city = spl[1]
                zp = spl[2].strip().split(" ")[1]
                state = spl[2].strip().split(" ")[0]
        return {"street": street, "city": city, "zip": zp, "state": state}

    result = []

    for ss in s:
        b = initSoup(ss)
        g = b.find("div", {"class": "column main_info"})
        name = g.find("h1").text.strip()
        url = ss
        addr = g.find("p", {"class": "content"}).text.strip()
        ad = parseAddress(addr)
        phone = g.find("li", {"class": "phone"}).text.strip().replace("Ph:", "")
        hours = g.find("li", {"class": "hours"}).text.strip().replace("Hours:", "")
        result.append(
            [
                locator_domain,
                url,
                name,
                ad["street"],
                ad["city"],
                ad["state"],
                ad["zip"],
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
