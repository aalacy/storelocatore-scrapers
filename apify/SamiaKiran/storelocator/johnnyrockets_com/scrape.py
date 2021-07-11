from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "johnnyrockets_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
}


DOMAIN = "https://www.johnnyrockets.com/https://goodnessme.ca/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        linklist = []
        token_url = "https://locations.johnnyrockets.com/"
        token = session.get(token_url, headers=headers)
        token = BeautifulSoup(token.text, "html.parser")
        token = token.select_one("script[src*=app]")['src']
        token = "https://locations.johnnyrockets.com/"+token
        log.info(token)
        log.info("Fetching the Token...")
        token = session.get(token, headers=headers)
        token = token.text.split('API_TOKEN",')[1].split(').')[0].replace('"',"")
        url = (
            "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token="
            + token
            + "&country=US&multi_account=true"
        )
        loclist = session.get(url, headers=headers).json()["locations"]
        headers2 = {
            "authorization": token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }
        for loc in loclist:
            location_type = loc["open_or_closed"]
            if "temp closed" in location_type:
                location_type = "Temporarily Closed"
            else:
                location_type = MISSING
            page_url = "https://locations.johnnyrockets.com" + loc["llp_url"]
            if page_url in linklist:
                continue
            linklist.append(page_url)
            log.info(page_url)
            loc = loc["store_info"]
            street_address = loc["address"]
            city = loc["locality"]
            state = loc["region"]
            try:
                API = (
                    "https://api.momentfeed.com/v1/analytics/api/llp.json?address="
                    + street_address
                    + "&locality="
                    + city
                    + "&region="
                    + state
                )
                temp = session.get(API, headers=headers2).json()[0]["store_info"]
            except:
                continue
            latitude = temp["latitude"]
            longitude = temp["longitude"]
            location_name = temp["name"]
            zip_postal = temp["postcode"]
            country_code = temp["country"]
            phone = temp["phone"]
            store_number = temp["corporate_id"]
            hours_of_operation = (
                (
                    temp["hours"]
                    .replace("1,", "Mon: ")
                    .replace("2,", " Tue: ")
                    .replace("3,", " Wed: ")
                    .replace("4,", " Thu: ")
                    .replace("5,", " Fri: ")
                    .replace("6,", " Sat: ")
                    .replace("7,", " Sun: ")
                )
                .replace(",", "-")
                .replace("00", ":00")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code.strip(),
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
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
