from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("multicare_org")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "Host": "www.bankpacificwest.com",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    }
    res = session.get(
        "https://www.bankpacificwest.com/Locations-Hours.aspx", headers=headers
    )
    soup = BeautifulSoup(res.text, "html.parser")
    trs = soup.find("body").find_all("tr")
    logger.info(len(trs))

    for tr in trs:
        tr = tr.find_all("td")[2]
        name = tr.find("h3").text.strip()
        all = str(tr.find("p")).replace("<p>", "").replace("</p>", "").split("<br/>")
        street = all[0]
        phone = all[2]
        tim = all[3].replace("Hours: ", "").replace("M-F,", "Monday - Friday: ")
        all = all[1].split(",")
        city = all[0]
        all = all[1].strip().split(" ")
        state = all[0]
        zip = all[1]

        yield SgRecord(
            locator_domain="https://www.bankpacificwest.com",
            page_url="https://www.bankpacificwest.com/Locations-Hours.aspxs",
            location_name=name,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<MISSING>",
            longitude="<MISSING>",
            hours_of_operation=tim.strip(),
        )


def scrape():
    write_output(fetch_data())


scrape()
