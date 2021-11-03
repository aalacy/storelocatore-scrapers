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
    locator_domain = "https://www.discounttirecenters.com/"
    missingString = "<MISSING>"

    def getAllStores():
        res = []
        s = bs4.BeautifulSoup(
            sgrequests.SgRequests()
            .get(
                "https://www.discounttirecenters.com/sitemap.xml",
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                },
            )
            .text,
            features="lxml",
        ).findAll("loc")
        for loc in s:
            if "store" in loc.text:
                if loc.text == "https://www.discounttirecenters.com/store-locations":
                    pass
                else:
                    res.append(loc.text)
        return res

    def initSoup(s):
        return bs4.BeautifulSoup(
            sgrequests.SgRequests()
            .get(
                s,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                },
            )
            .text,
            features="lxml",
        )

    def formatTime(string, day):
        return (
            string.strip()
            .replace(u"\n", u"")
            .replace(" : ", "")
            .replace(" :", "")
            .replace(": ", "")
            .replace("{}".format(day), "{} : ".format(day))
        )

    result = []

    for store in set(getAllStores()):
        s = initSoup(store)
        name = (
            s.findAll("span", {"class": "m-specific m-font-size-24 lh-1"})[0]
            .get_text(separator=" ")
            .strip()
        )
        street = s.find("font", {"class": "m-specific m-font-size-14 lh-1"}).get_text(
            separator=u"\n"
        )
        city = s.findAll("span", {"class": "font-size-14 lh-1"})
        state = s.findAll("span", {"class": "font-size-14 lh-1"})
        zp = s.findAll("span", {"class": "font-size-14 lh-1"})
        phone = s.findAll("font", {"class": "m-specific m-font-size-14 lh-1"})
        if len(street.split("\n")) > 0:
            street = street.split("\n")[0]
        if "433 E. Arrow Hwy. Azusa, CA 91702" in street:
            phone = phone[-1].get_text(separator="\n").split("\n")[-2]
            street = "433 E. Arrow Hwy."
            city = "Azusa"
            state = "CA"
            zp = "91702"
        if "934 N Victory Blvd, Burbank, CA 91502" in street:
            phone = phone[-1].get_text(separator="\n").split("\n")[-2]
            street = "934 N Victory Blvd"
            city = "Burbank"
            state = "CA"
            zp = "91502"
        if "21629 Sherman Way," in street:
            phone = phone[-1].get_text(separator="\n").split("\n")[-2]
            street = "21629 Sherman Way"
        if not city:
            if "https://www.discounttirecenters.com/store-el-monte" in store:
                phone = phone[-1].get_text(separator="\n").split("\n")[-2]
                city = "El Monte"
                state = (
                    s.findAll("span", {"class": "lh-1 font-size-14"})[1]
                    .text.split(",")[-1]
                    .strip()
                    .split(" ")[0]
                )
                zp = (
                    s.findAll("span", {"class": "lh-1 font-size-14"})[1]
                    .text.split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                )
            elif "https://www.discounttirecenters.com/store-canyon-country" in store:
                phone = phone[-1].get_text(separator="\n").split("\n")[-2]
                city = "Canyon Country"
                state = (
                    s.findAll("span", {"class": "lh-1 font-size-14"})[1]
                    .get_text(separator="\n")
                    .split("\n")[0]
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                )
                zp = (
                    s.findAll("span", {"class": "lh-1 font-size-14"})[1]
                    .get_text(separator="\n")
                    .split("\n")[0]
                    .split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                )
            else:
                city = (
                    s.find("span", {"style": "font-size: 14px;"})
                    .get_text(separator="\n")
                    .split("\n")[1]
                    .split(",")[0]
                )
                state = (
                    s.find("span", {"style": "font-size: 14px;"})
                    .get_text(separator="\n")
                    .split("\n")[-1]
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                )
                zp = (
                    s.find("span", {"style": "font-size: 14px;"})
                    .get_text(separator="\n")
                    .split("\n")[-1]
                    .split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                )
        elif city:
            if isinstance(city, list):
                if len(city) > 0:
                    if len(state[-1].get_text(separator="\n").split("\n")) == 2:
                        phone = (
                            state[-1].get_text(separator="\n").split("\n")[-1].strip()
                        )
                        zp = (
                            state[-1]
                            .get_text(separator="\n")
                            .split("\n")[-2]
                            .split(",")[-1]
                            .strip()
                            .split(" ")[-1]
                        )
                        state = (
                            state[-1]
                            .get_text(separator="\n")
                            .split("\n")[-2]
                            .split(",")[-1]
                            .strip()
                            .split(" ")[0]
                        )
                    else:
                        phone = phone[-1].get_text(separator="\n").split("\n")[-2]
                        zp = state[-1].text.split(",")[-1].strip().split(" ")[-1]
                        state = state[-1].text.split(",")[-1].strip().split(" ")[0]
                    city = (
                        city[-1].text.split(",")[0].replace("23051 Antonio Pkwy.", "")
                    )
            elif isinstance(city, str):
                city = city
        if "https://www.discounttirecenters.com/store-rancho-santa-margarita" in store:
            phone = (
                s.findAll("font", {"class": "m-specific m-font-size-14 lh-1"})[-1]
                .get_text(separator="\n")
                .split("\n")[-2]
            )
            zp = (
                s.findAll("span", {"style": "font-weight: inherit;"})[-1]
                .text.split(",")[-1]
                .strip()
                .split(" ")[-1]
            )
            state = (
                s.findAll("span", {"style": "font-weight: inherit;"})[-1]
                .text.split(",")[-1]
                .strip()
                .split(" ")[0]
            )
        timeArray = []
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Monday"}).get_text(separator=" : "), "Monday"
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Tuesday"}).get_text(separator=" : "), "Tuesday"
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Wednesday"}).get_text(separator=" : "),
                "Wednesday",
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Thursday"}).get_text(separator=" : "), "Thursday"
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Friday"}).get_text(separator=" : "), "Friday"
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Saturday"}).get_text(separator=" : "), "Saturday"
            )
        )
        timeArray.append(
            formatTime(
                s.find("div", {"id": "Sunday"}).get_text(separator=" : "), "Sunday"
            )
        )
        hours = ", ".join(timeArray)
        a = s.findAll("a", href=True)
        lat = missingString
        lng = missingString
        for aa in a:
            if "https://www.google.com/maps/dir//" in aa["href"]:
                latlng = (
                    aa["href"]
                    .replace("https://www.google.com/maps/dir//", "")
                    .split("/")[1]
                    .replace("@", "")
                    .split(",")
                )
                lat = latlng[0]
                lng = latlng[1]
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
                lat,
                lng,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
