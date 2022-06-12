import json
import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "9round_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.9round.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.9round.com/locations/directory"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("li", {"class": "pb-1"})
        for loc in loclist:
            url = "https://www.9round.com" + loc.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            state_list = soup.findAll("a", {"class": "lead"})
            for link in state_list:
                page_url = "https://www.9round.com" + link["href"]
                r = session.get(page_url, headers=headers)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    log.info(page_url)
                    try:
                        temp = r.text.split("<script type='application/ld+json'>")[
                            1
                        ].split("</script>", 1)[0]
                        temp = json.loads(temp)
                        location_name = html.unescape(temp["name"])
                        latitude = temp["geo"]["latitude"]
                        longitude = temp["geo"]["longitude"]
                        hours_of_operation = temp["openingHours"]
                        try:
                            phone = (
                                soup.select_one("a[href*=tel]")
                                .text.replace("\n", "")
                                .replace("Call: ", "")
                            )
                        except:
                            phone = MISSING
                        street_address = html.unescape(temp["address"]["streetAddress"])
                        city = html.unescape(temp["address"]["addressLocality"])
                        state = temp["address"]["addressRegion"]
                        zip_postal = temp["address"]["postalCode"]
                    except:
                        try:
                            address = soup.find("li", {"class": "pb-1"}).text
                            location_name = soup.find("h2").text.replace("\n", "")
                        except:
                            address = link.text
                            location_name = MISSING
                        address = address.split("-")
                        street_address = address[1]
                        if "," in address[0]:
                            address = address[0].split(",")
                        else:
                            address = address[0].split()
                        city = address[0]
                        state = address[1]
                        zip_postal = MISSING
                        phone = MISSING
                        hours_of_operation = MISSING
                        latitude = MISSING
                        longitude = MISSING
                    country_code = "US"
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
                        phone=phone,
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation.strip(),
                    )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
