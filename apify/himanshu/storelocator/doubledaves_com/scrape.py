from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "doubledaves_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://doubledaves.com/"
MISSING = "<MISSING>"


def fetch_data():
    addressess = []
    base_url = "https://www.doubledaves.com"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"class": "dropdown location-dropdown"}).find_all("a")
    del main[-1]
    for atag in main:
        r1 = session.get(base_url + atag["href"])
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1 = soup1.find("div", {"class": "location-grid"}).find_all(
            "a", text="Website"
        )

        for weblink in main1:
            r2 = session.get(base_url + weblink["href"])
            page_url = base_url + weblink["href"]
            log.info(page_url)
            if "Coming soon" in r2.text:
                continue
            soup2 = BeautifulSoup(r2.text, "lxml")
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
