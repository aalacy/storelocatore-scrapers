from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "craftrepublic_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

headers2 = {
    "authority": "api.momentfeed.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.craftrepublic.com",
    "referer": "https://www.craftrepublic.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}

DOMAIN = "https://www.craftrepublic.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.craftrepublic.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "locationLink"})
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            location_name = loc.text
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = soup.find("div", {"class": "locations-address"})
            latitude, longitude = (
                address.find("a")["href"].split("Location/")[1].split("+,")
            )
            address = address.find("p").get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            phone = soup.select_one("a[href*=tel]").text
            token = r.text.split('"locId": "')[1].split('"')[0]
            api_url = "https://api.momentfeed.com/v1/lf/location/store-info/" + token
            r = session.get(api_url, headers=headers2)
            if r.status_code != 200:
                hours_of_operation = MISSING
            else:
                hours = r.json()["hours"]
                hours = hours.rstrip(";")
                hours = hours.split(";")
                hours_of_operation = ""
                for h in hours:
                    h = h.strip()
                    m = h.split(",")
                    if m[0] == "1":
                        day = "Monday"
                    elif m[0] == "2":
                        day = "Tuesday"
                    elif m[0] == "3":
                        day = "Wednesday"
                    elif m[0] == "4":
                        day = "Thursday"
                    elif m[0] == "5":
                        day = "Friday"
                    elif m[0] == "6":
                        day = "Saturday"
                    elif m[0] == "7":
                        day = "Sunday"
                    start_t = m[1]
                    end_t = m[2]
                    hours_of_operation = (
                        hours_of_operation + " " + day + ": " + start_t + "-" + end_t
                    )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
