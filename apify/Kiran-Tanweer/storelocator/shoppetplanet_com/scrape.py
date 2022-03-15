from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "shoppetplanet_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

url = "https://ecomca.franpos.com/api/v2/store/102166"


headers_2 = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "origin": "https://cart.shoppetplanet.com",
    "referer": "https://cart.shoppetplanet.com/",
}


DOMAIN = "https://www.shoppetplanet.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.shoppetplanet.com/store-locations/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locs = soup.findAll("li", {"class": "sl-region"})
    for loc in locs:
        try:
            page_url = loc.find("a")["href"]
        except:
            continue
        log.info(page_url)
        if page_url.split("/")[-1].isdigit():
            api_url = (
                "https://ecomca.franpos.com/api/v2/store/" + page_url.split("/")[-1]
            )
            temp = session.post(api_url, headers=headers_2).json()["data"]
            location_name = temp["name"]
            phone = temp["phone"]
            address = temp["location"]
            latitude = address["latitude"]
            longitude = address["longitude"]
            try:
                street_address = address["address"] + " " + address["address2"]
            except:
                street_address = address["address"]
            city = address["city"]
            state = address["stateProvince"]["name"]
            zip_postal = address["zipPostal"]
            country_code = address["country"]["abbreviation"]
            hours_of_operation = (
                str(temp["workingHours"])
                .replace("': '", " ")
                .replace("', '", " ")
                .replace("{'", "")
                .replace("'}", "")
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
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        else:
            r = session.get(page_url, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            location_name = bs.find("h1", {"class": "store-title"}).text
            address = bs.findAll("div", {"class": "addy1"})
            if len(address) == 4:
                street = address[0].text + " " + address[1].text
                locality = address[2].text
                zip_postal = address[3].text
            else:
                street = address[0].text
                locality = address[1].text
                zip_postal = address[2].text
            city, state = locality.split(",")
            if zip_postal.isdigit():
                country_code = "US"
            else:
                country_code = "CA"
            phone = bs.find("p", {"class": "store-info"}).find("a").text
            hours = bs.find("p", {"class": "store-hours"}).text
            hours = hours.replace("\n", " ")
            hours_of_operation = hours.split("Holidays :")[0].strip()
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
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
