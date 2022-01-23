import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "long-mcquade_com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.long-mcquade.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.long-mcquade.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.long-mcquade.com/locations/alberta/",
    "accept-language": "en-US,en;q=0.9",
}
DOMAIN = "https://long-mcquade.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.long-mcquade.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("select", {"id": "select-province"}).findAll("option")
        for state in statelist[1:]:
            state_id = state["value"]
            data = {"action": "getStoresByProvinceId", "provinceId": state_id}
            url = "https://www.long-mcquade.com/includes/AjaxFunctions.php"
            loclist = session.post(url, data=data, headers=headers).json()[1:]
            for loc in loclist:
                page_url = "https:" + loc["url"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h1").text
                location_name = strip_accents(location_name)
                temp = (
                    soup.findAll("table", {"class": "table"})[1].find("tr").find("td")
                )
                phone = temp.select("a[href*=tel]")[0].text
                temp = temp.get_text(separator="|", strip=True).split("|")
                street_address = temp[0]
                street_address = strip_accents(street_address)
                address = temp[1].split(",")
                city = address[0]
                city = strip_accents(city)
                state = address[1]
                state = strip_accents(state)
                zip_postal = address[2]
                country_code = "CA"
                hours_of_operation = (
                    temp[-7]
                    + " "
                    + temp[-6]
                    + " "
                    + temp[-5]
                    + " "
                    + temp[-4]
                    + " "
                    + temp[-3]
                    + " "
                    + temp[-2]
                    + " "
                    + temp[-1]
                )
                hours_of_operation = strip_accents(hours_of_operation)
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name.strip(),
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
