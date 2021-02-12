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
    locator_domain = "https://www.lacolombe.com/"
    missingString = "<MISSING>"

    def retrieveStoreCards():
        url = "https://www.lacolombe.com/pages/cafes"
        s = bs4.BeautifulSoup(sgrequests.SgRequests().get(url).text, features="lxml")
        res = []
        for card in s.findAll("div", {"class": "location-card"}):
            name = card.find("img", {"class": "location-card__header__img"})["alt"]
            cardLoc = (
                card.find("a", {"class": "link-quiet"})
                .get_text(separator="%")
                .split("%")
            )
            street = cardLoc[0]
            city = cardLoc[1].split(",")[0]
            city_zp = cardLoc[1].replace(city, "").replace(",", "", 1).strip().split()
            if "Suite" in cardLoc[1]:
                street = cardLoc[0].strip() + " " + cardLoc[1].strip()
                city = cardLoc[2].split(",")[0]
                city_zp = (
                    cardLoc[2].replace(city, "").replace(",", "", 1).strip().split()
                )
            if "Chicago IL 60614" in city:
                city = cardLoc[1].split(" ")[0]
                city_zp = (
                    cardLoc[1].replace(city, "").replace(",", "", 1).strip().split()
                )
            if "Seven Bryant Park Building" in city:
                city = cardLoc[3].split(",")[0]
                city_zp = (
                    cardLoc[3].replace(city, "").replace(",", "", 1).strip().split()
                )
            if "(SW Corner of 6th & Market)" in city:
                city = cardLoc[2].split(",")[0]
                city_zp = (
                    cardLoc[2].replace(city, "").replace(",", "", 1).strip().split()
                )
            state = city_zp[0]
            zp = city_zp[1]
            phone = s.find("div", {"class": "location-card__phone"}).find("a").text
            datetime = (
                str(s.find("dl", {"class": "location-card__hours__list"}))
                .replace("<dt>", "")
                .replace("<dd>", "")
                .replace("</dt>", "")
                .replace("</dd>", "")
                .replace('<dl class="location-card__hours__list">', "")
                .replace("</dl>", "")
                .split(u"\n")
            )
            datetime = list(filter(None, datetime))
            datetime = [": ".join(x) for x in zip(datetime[0::2], datetime[1::2])]
            hours = ", ".join(datetime)
            latlng = (
                s.find(
                    "a",
                    {"class": "btn btn-primary btn--small location-card__footer__btn"},
                )["href"]
                .replace("https://www.google.com/maps/place/", "")
                .split("/")[1]
                .split(",")
            )
            lat = latlng[0].replace("@", "")
            lng = latlng[1]
            res.append(
                {
                    "locator_domain": locator_domain,
                    "page_url": missingString,
                    "location_name": name,
                    "street_address": street,
                    "city": city,
                    "state": state,
                    "zip": zp,
                    "country_code": missingString,
                    "store_number": missingString,
                    "phone": phone,
                    "location_type": missingString,
                    "lat": lat,
                    "lng": lng,
                    "hours": hours,
                }
            )
        return res

    stores = retrieveStoreCards()

    result = []

    for s in stores:
        result.append(
            [
                s["locator_domain"],
                s["page_url"],
                s["location_name"],
                s["street_address"],
                s["city"],
                s["state"],
                s["zip"],
                s["country_code"],
                s["store_number"],
                s["phone"],
                s["location_type"],
                s["lat"],
                s["lng"],
                s["hours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
