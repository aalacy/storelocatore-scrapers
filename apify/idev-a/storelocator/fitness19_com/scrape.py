import csv
import dirtyjson
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

session = SgRequests()


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
    base_url = "https://www.fitness19.com"
    r = session.get(
        "https://www.fitness19.com/convenient-locations",
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Cookie": "PHPSESSID=3185ede2083d428813574cfff3f54e86; _ga=GA1.2.2122691975.1609175180; _gid=GA1.2.223037308.1609175180; hubspotutk=e6bbd642567c41b18f38943afd8b50c8; __hssrc=1; _fbp=fb.1.1609185727776.1823918006; __hstc=93906690.e6bbd642567c41b18f38943afd8b50c8.1609175181819.1609189082777.1609226459278.4; _gat_gtag_UA_34143267_1=1; __hssc=93906690.2.1609226459278",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        },
    )
    soup = bs(r.text, "lxml")
    links = soup.select("section#location-list a")

    data = []
    for link in links:
        locations_by_state_url = link["href"]
        r1 = session.get(locations_by_state_url)
        soup1 = bs(r1.text, "lxml")
        location_links = soup1.select(
            "section#locations_list p.location_link a:nth-child(3)"
        )
        for location_link in location_links:
            page_url = location_link["href"]
            if page_url == "https://www.fitness19.com/centers/rancho-cucamonga-ii/":
                page_url = "https://www.fit19.com/locations/rancho-cucamonga-2"
            r2 = session.get(page_url)
            soup2 = bs(r2.text, "lxml")
            try:
                store = dirtyjson.loads(
                    r2.text.split('<script type="application/ld+json">')[1]
                    .split("</script>")[0]
                    .replace("\n", "")
                )
                location_name = soup2.select_one("section#location-title h1").string
                phone = store["telephone"]
                street_address = store["address"]["streetAddress"]
                city = store["address"]["addressLocality"]
                zip = store["address"]["postalCode"]
                state = store["address"]["addressRegion"]
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                geo = (
                    r2.text.split("new google.maps.LatLng(")[1].split(")")[0].split(",")
                )
                latitude = geo[0].strip() or "<MISSING>"
                longitude = geo[1].strip() or "<MISSING>"
                hours_of_operation = (
                    soup2.select_one("section#location-hours dl")
                    .text.replace("\n", "")
                    .strip()
                )
            except:
                store = dirtyjson.loads(
                    r2.text.split("window.local = ")[1]
                    .split("window.managers")[0]
                    .replace("\r", "")
                    .replace("\n", "")
                    .strip()
                )
                location_name = store["name"]
                phone = store["phone_number"]
                street_address = store["address"]
                city = store["city"]
                state = store["state"]
                zip = store["zip"]
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                latitude = store["geolocation"]["lat"]
                longitude = store["geolocation"]["long"]
                hours_of_operation = (
                    bs(store["gym_hours"], "lxml").text.replace("\n", "").strip()
                )
            country_code = "US"
            if "Permanently" in hours_of_operation:
                continue

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
