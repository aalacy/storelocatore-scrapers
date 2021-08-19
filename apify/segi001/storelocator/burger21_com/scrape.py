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
    locator_domain = "https://www.burger21.com/"
    missingString = "<MISSING>"

    def sendreq(l):
        return req.Req().get(l)

    def initSoup(l):
        return bs4.BeautifulSoup(sendreq(l).text, features="lxml")

    def allStores():
        b = initSoup("https://www.burger21.com/locations/")
        r = []
        for e in b.findAll("div", {"class": "location-item"}):
            a = e.find("h2").find("a")["href"]
            r.append(a)
        return r

    s = allStores()
    result = []

    for ss in s:
        b = initSoup(ss)
        g = b.find("div", {"class": "location-slide-wrap"})
        name = g.find("h1").text.strip()
        link = ss
        addr = g.find("h2").get_text(separator="\n").split("\n")
        street = addr[0]
        city = addr[1].split(",")[0].strip()
        state = addr[1].split(",")[1].strip().split(" ")[0]
        if len(addr) == 3:
            if len(addr[1].split(",")[1].strip().split(" ")) == 2:
                zp = addr[1].split(",")[1].strip().split(" ")[1]
            else:
                zp = missingString
        elif len(addr) == 2:
            zp = missingString
        phone = addr[-1].strip().replace("P:", "").strip()
        if "Tampa,  FL 33607" in phone:
            phone = missingString
            zp = "33607"
        if "Tampa International Airport,  Tampa" in phone:
            phone = missingString
        timeArr = list(
            filter(
                None,
                g.find("div", {"class": "store-hours"})
                .text.strip()
                .replace(
                    "Our patios + dining rooms are open, complying with all state and local regulations.",
                    "",
                )
                .replace("INDOOR DINING AREA IS OPEN", "")
                .replace("CURRENT HOURS:", "")
                .replace("oo", "00")
                .replace("We’re Open:", "")
                .split("\n"),
            )
        )
        hours = ", ".join(timeArr).replace(u"\xa0", u" ")
        result.append(
            [
                locator_domain,
                link,
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
