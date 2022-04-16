from sglogging import sglog
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "doubledaves.com"
BASE_URL = "https://www.doubledaves.com"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
session = SgRequests()
website = "doubledaves_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    addressess = []
    soup = pull_content(BASE_URL)
    main = soup.find("div", {"class": "dropdown location-dropdown"}).find_all("a")
    del main[-1]
    for atag in main:
        url = BASE_URL + atag["href"]
        soup1 = pull_content(url)
        try:
            main1 = soup1.find("div", {"class": "location-grid"}).find_all(
                "a", text="Website"
            )
        except:
            continue
        for weblink in main1:
            page_url = BASE_URL + weblink["href"]
            r2 = session.get(page_url)
            log.info(page_url)
            if "Coming soon" in r2.text:
                continue
            soup2 = bs(r2.text, "lxml")
            temp = r2.text.split(weblink["href"])[-1].split("locations.push(store);")[0]
            store_number = temp.split("store['id'] = ")[1].split(";")[0]
            latitude = temp.split("store['latitude'] = ")[1].split(";")[0]
            longitude = temp.split("store['longitude'] = ")[1].split(";")[0]
            location_name = (
                soup2.find("div", {"class": "page-heading"}).find("h1").text.strip()
            )
            main2 = soup2.find("div", {"class": "location-hours"}).find_all("p")
            if len(main2) == 2:
                loc_address = list(main2[1].stripped_strings)
                phone = main2[0].text.strip().replace("- ", "")
            else:
                loc_address = list(main2[0].stripped_strings)
                phone = "<MISSING>"
            street_address = loc_address[0].strip()
            if street_address in addressess:
                continue
            addressess.append(street_address)
            city = loc_address[1].strip().split(",")[0].strip()
            state = loc_address[1].strip().split(",")[1].strip().split(" ")[0].strip()
            zip_postal = (
                loc_address[1].strip().split(",")[1].strip().split(" ")[1].strip()
            )
            if soup2.find("div", {"class": "hours grid-cell"}):
                mainhour = soup2.find("div", {"class": "hours grid-cell"}).find_all(
                    "div", {"class": "grid no-wrap desktop-collapse only-desktop"}
                )
                title = list(mainhour[0].stripped_strings)
                h = ""
                h1 = ""
                head = title[0]
                if len(title) == 2:
                    head2 = title[1]
                del mainhour[0]
                for hr in mainhour:
                    hr1 = list(hr.stripped_strings)
                    h += hr1[0] + ":" + hr1[1] + " "
                    if len(title) == 2:
                        if len(hr1) == 3:
                            h1 += hr1[0] + ":" + hr1[2] + " "
                hour = head + " = " + h
                if len(title) == 2:
                    hour += hour + head2 + " = " + h1
            else:
                hour = "<MISSING>"
            hour = hour.replace("Dough Slingin' Hours = ", "").replace("::", " ")
            country_code = "US"
            phone = phone.replace("DAVE", "").replace("- ", "")
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hour.strip(),
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
