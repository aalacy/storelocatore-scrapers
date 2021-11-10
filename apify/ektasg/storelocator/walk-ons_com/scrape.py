from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests, SgRequestError
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "walk-ons_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://walk-ons.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://walk-ons.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("div", {"class": "locationList collapse"})
    for link in linklist:
        loclist = link.findAll("div", {"class": "locationItem"})
        for loc in loclist:
            link = loc.find("a")
            location_name = link.text
            link = link["href"]
            if (
                link.find("locations.walk-ons.com") == -1
                and "Viera, FL" in location_name
            ):
                log.info(link)
                temp = loc.findAll("div")
                address = temp[0].get_text(separator="|", strip=True).split("|")
                street_address = address[1]
                phone = address[-1]
                address = address[2].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = (
                    temp[7]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Hours", "")
                )

            elif link.find("locations.walk-ons.com") == -1:
                continue
            else:
                log.info(link)
                phone = soup.select_one("a[href*=tel]").text
                try:
                    r = SgRequests.raise_on_err(session.get(link, headers=headers))
                    soup = BeautifulSoup(r.text, "html.parser")
                    street_address = soup.find(
                        "span", {"class": "c-address-street-1"}
                    ).text
                    city = soup.find("span", {"class": "c-address-city"}).text
                    state = soup.find("span", {"class": "c-address-state"}).text
                    zip_postal = soup.find(
                        "span", {"class": "c-address-postal-code"}
                    ).text
                    phone = soup.select_one("a[href*=tel]").text
                    latitude = str(soup).split("lat: ", 1)[1].split(",", 1)[0]
                    longitude = str(soup).split("lng: ", 1)[1].split(",", 1)[0]
                    country_code = "US"
                    hour_list = soup.find("tbody", {"class": "hours-body"}).findAll(
                        "tr"
                    )
                    hours_list = []
                    for hour in hour_list:
                        hour = hour.findAll("td")
                        day = hour[0].text
                        time = hour[1].text
                        hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()
                except SgRequestError as e:
                    log.error(e.message)
                    continue

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
