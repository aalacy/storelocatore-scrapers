import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "moosejaw_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "authority": "www.moosejaw.com",
    "method": "GET",
    "path": "/content/find-a-shop",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": 'Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://www.moosejaw.com/content/find-a-shop"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("td", {"class": "shopname"})
        for loc in loclist:
            link = loc.find("a")["href"]
            link = "https://www.moosejaw.com" + link
            r = session.get(link, headers=headers)
            coords = r.text.split("LatLng(")[1].split(")", 1)[0]
            coords = coords.split(",")
            lat = coords[0]
            longt = coords[1]
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("h2").text
            try:
                street = soup.find("span", {"itemprop": "streetAddress"}).text
            except:
                street = soup.find("p", {"itemprop": "streetAddress"}).text
            city = soup.find("span", {"itemprop": "addressLocality"}).text
            state = soup.find("span", {"itemprop": "addressRegion"}).text
            pcode = soup.find("span", {"itemprop": "postalCode"}).text
            try:
                phone = soup.find("span", {"itemprop": "telephone"}).text
            except:
                phone = soup.find("p", {"itemprop": "telephone"}).text
            hours = (
                soup.find("div", {"class": "store-hours"})
                .find("p")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            final_data.append(
                [
                    "https://www.moosejaw.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
