import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

DOMAIN = "https://mastercuts.com"
MISSING = "<MISSING>"

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
HEADERS = {"User-Agent": user_agent}

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    data = []
    storelist = []
    url = "https://www.signaturestyle.com/salon-directory.html"
    response = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    loclist = soup.select("a[href*=locations]")
    for loc_url in loclist:
        loc_url = "https://www.signaturestyle.com" + loc_url["href"]

        if "pr.html" in loc_url:
            continue
        res = session.get(loc_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        linklist = soup.select("a[href*=haircuts]")
        for link in linklist:
            link = "https://www.signaturestyle.com" + link["href"]
            r = session.get(link, headers=HEADERS)
            loc_data = BeautifulSoup(r.text, "html.parser")
            loc_soup = loc_data.find(class_="salondetailspagelocationcomp")
            try:
                location_name = loc_data.find("h2").text.strip()
                country = "US"

                hours_of_operation = " ".join(
                    list(loc_soup.find(class_="salon-timings").stripped_strings)
                )
            except:
                continue
            phone = loc_soup.find(id="sdp-phone").text.strip()
            street_address = loc_soup.find(
                "span", attrs={"itemprop": "streetAddress"}
            ).text.strip()
            city = loc_soup.find(
                "span", attrs={"itemprop": "addressLocality"}
            ).text.strip()
            state = loc_soup.find(
                "span", attrs={"itemprop": "addressRegion"}
            ).text.strip()
            zipcode = loc_soup.find(
                "span", attrs={"itemprop": "postalCode"}
            ).text.strip()
            lat = loc_data.find("meta", attrs={"itemprop": "latitude"})["content"]
            lon = loc_data.find("meta", attrs={"itemprop": "longitude"})["content"]
            store_number = link.split("-")[-1].split(".")[0]
            location_type = "<MISSING>"

            if " " in zipcode:
                country = "CA"
            if len(hours_of_operation) < 3:
                hours_of_operation = "<MISSING>"
            if store_number in storelist:
                continue
            storelist.append(store_number)
            data.append(
                [
                    DOMAIN,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    store_number,
                    phone,
                    location_type,
                    lat,
                    lon,
                    hours_of_operation,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
