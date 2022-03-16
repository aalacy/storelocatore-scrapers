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
    locator_domain = "https://baileysgym.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initSoup(l):
        r = req(l)
        return [r, bs4.BeautifulSoup(r.text, features="lxml")]

    def getAllStoreLinks():
        s = initSoup("https://baileysgym.com/page/Locations.aspx")[1]
        l = s.findAll("div", {"class": "location-list"})
        res = []
        for e in l:
            if not e.find("div").find("a"):
                pass
            else:
                res.append(e.find("div").find("a")["href"])
        return res

    s = set(getAllStoreLinks())

    result = []

    for slug in s:
        l = "{}{}".format(locator_domain, slug.replace("/", "", 1))
        re = initSoup(l)[1]
        name = re.find("h1", {"id": "ctl00_cphBody_h1Title"}).text
        location_details = re.find("div", {"class": "location-details"}).findAll("div")[
            1
        ]
        addr = location_details.findAll("strong")[0]
        street = missingString
        zp = missingString
        state = missingString
        city = missingString
        phone = (
            location_details.findAll("strong")[2]
            .text.strip()
            .replace("(", "")
            .replace(")", "")
        )
        if "Address:" in addr.text:
            addr = location_details.findAll("strong")[1]
        marker = addr.text
        i = len(marker.split(","))
        if i == 1:
            street = marker.split(",")[0]
            act_addr = location_details.findAll("strong")[2].text
            phone = (
                location_details.findAll("strong")[3]
                .text.strip()
                .replace("(", "")
                .replace(")", "")
            )
            spli = act_addr.split(",")
            if len(spli) == 2:
                city = spli[0].strip()
                state = spli[1].strip().split(" ")[0].replace(u"\xa0", "")
                zp = spli[1].strip().split(" ")[-1]
            else:
                splitt = act_addr.split(" ")
                city = splitt[0]
                state = splitt[1].replace(u"\xa0", "")
                zp = splitt[-1]
        else:
            if "Unit" in marker.split(",")[-1]:
                street = marker
                ac_addr = location_details.findAll("strong")[1].text
                phone = (
                    location_details.findAll("strong")[3]
                    .text.strip()
                    .replace("(", "")
                    .replace(")", "")
                )
                spli = list(filter(None, ac_addr.split(" ")))
                zp = spli[-1]
                state = spli[-2].replace(u"\xa0", "")
                city = spli[0]
            else:
                spl = marker.split(",")
                zp = spl[1].strip().split(" ")[-1]
                state = spl[1].strip().split(" ")[-2]
                if "ORANGE PARK" in spl[0]:
                    city = "ORANGE PARK"
                elif "JACKSONVILLE" in spl[0]:
                    city = "JACKSONVILLE"
                elif "BRUNSWICK" in spl[0]:
                    city = "BRUNSWICK"
                else:
                    city = spl[0].split(" ")[-1]
                street = (
                    marker.replace(",", "")
                    .replace(city, "")
                    .replace(state, "")
                    .replace(zp, "")
                    .strip()
                )
        if phone == "":
            phone = (
                location_details.findAll("strong")[2]
                .text.strip()
                .replace("(", "")
                .replace(")", "")
            )
        if "FL" in phone:
            phone = (
                location_details.findAll("strong")[4]
                .text.strip()
                .replace("(", "")
                .replace(")", "")
            )
        if "TBA" in phone:
            phone = missingString
        if "Fax" in phone:
            phone = (
                location_details.findAll("strong")[3]
                .text.strip()
                .replace("(", "")
                .replace(")", "")
            )
        result.append(
            [
                locator_domain,
                l,
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
                missingString,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
