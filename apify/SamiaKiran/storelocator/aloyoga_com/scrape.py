import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "aloyoga_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.aloyoga.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.aloyoga.com/pages/stores"
        r = session.get(url, headers=headers)
        api_key = r.text.split("apiKey=", 1)[1].split("shop=")[0].replace("\\u0026", "")
        API_ENDPOINT = (
            "https://cdn.builder.io/api/v1/query/"
            + api_key
            + "/web-component-page?omit=meta.componentsUsed&apiKey="
            + api_key
            + "&userAttributes.urlPath=%2Fpages%2Fstores&userAttributes.host=www.aloyoga.com&userAttributes.device=desktop&userAttributes.locale=en-US&options.web-component-page.prerender=true"
        )
        r = session.get(API_ENDPOINT, headers=headers).json()["web-component-page"][0][
            "data"
        ]["html"]
        loclist = r.split("</picture>")[2:-1]
        for loc in loclist:
            loc = BeautifulSoup(loc, "html.parser")
            page_url = loc.find("a")["href"]
            log.info(page_url)
            loc = loc.findAll("span")
            location_name = loc[0].get_text(separator="|", strip=True).replace("|", "")
            address = loc[3].get_text(separator="|", strip=True).replace("|", " ")
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
            phone = loc[5].get_text(separator="|", strip=True).replace("|", "")
            hours_of_operation = (
                loc[7].get_text(separator="|", strip=True).replace("|", " ")
            )
            if "Studio" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Studio")[0]
            elif "Our" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Our")[0]
            if hours_of_operation == "HOURS":
                hours_of_operation = (
                    loc[8].get_text(separator="|", strip=True).replace("|", " ")
                )
            country_code = "US"
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
