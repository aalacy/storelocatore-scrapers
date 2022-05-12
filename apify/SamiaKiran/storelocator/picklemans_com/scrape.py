import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "picklemans_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.picklemans.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/1554/stores.js?callback=SMcallback2"
        r = session.get(url, headers=headers)
        loclist = json.loads(r.text.split("SMcallback2(")[1].split("}]})")[0] + "}]}")[
            "stores"
        ]
        for loc in loclist:
            if "COMING SOON" in loc["description"]:
                continue
            location_name = BeautifulSoup(loc["name"], "html.parser").text
            store_number = loc["id"]
            phone = loc["phone"]
            address = BeautifulSoup(loc["address"], "html.parser")
            page_url = address.find("a")["href"]
            if "picklemans" not in page_url:
                page_url = DOMAIN + address.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                day = soup.find("span", {"itemprop": "dayOfWeek"}).text
                opens = soup.find("span", {"itemprop": "opens"}).text
                closes = soup.find("span", {"itemprop": "closes"}).text
                hours_of_operation = day + " " + opens + "-" + closes
            except:
                try:
                    hours_of_operation = (
                        soup.findAll("bd1")[-1]
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("\n", " ")
                        .split("Hours:")[1]
                    )
                except:
                    hours_of_operation = (
                        soup.findAll("bd1")[0]
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("\n", " ")
                        .split("Hours:")[1]
                    )

            address = address.get_text(separator="|", strip=True).replace("|", " ")
            address = address.replace(",", " ")
            address = usaddress.parse(address)
            i = 0
            street_address = ""
            city = ""
            state = ""
            zip_postal = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street_address = street_address + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    zip_postal = zip_postal + " " + temp[0]
                i += 1
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            if "None" in hours_of_operation:
                hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
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
