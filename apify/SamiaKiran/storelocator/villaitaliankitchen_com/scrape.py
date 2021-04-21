from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "villaitaliankitchen.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    linklist = []
    url = "https://locations.villaitaliankitchen.com/US.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("ul", {"class": "c-directory-list-content"}).findAll("li")
    for loc in loclist:
        no = loc.find("span", {"class": "c-directory-list-content-item-count"}).text
        page_url = loc.find("a")["href"]
        page_url = "https://locations.villaitaliankitchen.com/" + page_url
        if no == "(1)":
            linklist.append(page_url)
        else:

            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                temp_list = soup.find(
                    "ul", {"class": "c-directory-list-content"}
                ).findAll("li")
            except:
                temp_list = soup.findAll("div", {"class": "c-location-grid-item"})
            for temp in temp_list:
                try:
                    no = temp.find(
                        "span", {"class": "c-directory-list-content-item-count"}
                    ).text
                except:
                    no = "(1)"
                try:
                    page_url = temp.find("a")["href"]
                except:
                    page_url = temp.find("a", {"class": "c-location-grid-item-link"})[
                        "href"
                    ]
                page_url = (
                    "https://locations.villaitaliankitchen.com"
                    + page_url.replace("..", "")
                )
                if no == "(1)":
                    linklist.append(page_url)
                else:
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    for x in soup.find(
                        "div", {"class": "container location-list-container"}
                    ).findAll("div", {"class": "c-location-grid-col col-sm-4"}):
                        page_url = x.find("a", {"class": "c-location-grid-item-link"})[
                            "href"
                        ]
                        page_url = (
                            "https://locations.villaitaliankitchen.com/"
                            + page_url.replace("../", "")
                        )
                        linklist.append(page_url)

    for link in linklist:
        log.info(link)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        location_name = soup.find(
            "span", {"class": "location-name-geomodifier uppercase"}
        ).text
        street_address = soup.find(
            "span", {"class": "c-address-street c-address-street-1"}
        ).text
        city = soup.find("span", {"class": "c-address-city"}).text.replace(",", "")
        state = soup.find("abbr", {"class": "c-address-state"}).text
        zip_postal = soup.find("span", {"class": "c-address-postal-code"}).text
        phone = soup.find("span", {"itemprop": "telephone"}).text
        hour_list = soup.find("table", {"class": "c-location-hours-details"}).findAll(
            "tr"
        )
        hours_of_operation = " ".join(
            hour.get_text(separator="|", strip=True).replace("|", " ")
            for hour in hour_list
        )
        coords = soup.find("span", {"class": "coordinates"})
        latitude = coords.find("meta", {"itemprop": "latitude"})["content"]
        longitude = coords.find("meta", {"itemprop": "longitude"})["content"]
        yield SgRecord(
            locator_domain="https://villaitaliankitchen.com/",
            page_url=link,
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
