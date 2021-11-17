import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "americasmattress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.americasmattress.com"
MISSING = SgRecord.MISSING

token_url = "https://www.americasmattress.com/springfield-il/locations"
r = session.get(token_url)
soup = BeautifulSoup(r.text, "html.parser")
token = soup.find("meta", {"name": "csrf-token"})["content"]


headers = {
    "Connection": "keep-alive",
    "Content-Length": "0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "*/*",
    "X-CSRF-Token": token,
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.americasmattress.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.americasmattress.com/springfield-il/locations",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_data():
    if True:
        url = "https://www.americasmattress.com/springfield-il/locations/finderajax"
        loclist = session.post(url, headers=headers).json()
        for loc in loclist:
            latitude = loc["latitude"]
            longitude = loc["longtitude"]
            store_number = loc["id"]
            location_name = loc["name"]
            page_url = DOMAIN + loc["url"]
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zipcode"]
            street_address = loc["address"]
            phone = loc["phone"]
            log.info(page_url)

            try:
                loc = json.loads(loc["hours"])

                if loc["monday"]["open"] is None:
                    mon = " Mon Closed"
                else:
                    mon = "Mon " + loc["monday"]["open"] + "-" + loc["monday"]["close"]
                if loc["tuesday"]["open"] is None:
                    tue = " Tue Closed"
                else:
                    tue = (
                        " Tue " + loc["tuesday"]["open"] + "-" + loc["tuesday"]["close"]
                    )
                if loc["wednesday"]["open"] is None:
                    wed = " Wed Closed"
                else:
                    wed = (
                        " Wed "
                        + loc["wednesday"]["open"]
                        + "-"
                        + loc["wednesday"]["close"]
                    )
                if loc["thursday"]["open"] is None:
                    thu = " Thu Closed"
                else:
                    try:
                        thu = (
                            " Thu "
                            + loc["thursday"]["open"]
                            + "-"
                            + loc["thursday"]["close"]
                        )
                    except:
                        thu = (
                            " Thu "
                            + loc["thursday"]["open"]
                            + "-"
                            + loc["wednesday"]["close"]
                        )
                if loc["friday"]["open"] is None:
                    fri = " Fri Closed"
                else:
                    fri = " Fri " + loc["friday"]["open"] + "-" + loc["friday"]["close"]
                if loc["saturday"]["open"] is None:
                    sat = " Sat Closed"
                else:
                    sat = (
                        " Sat "
                        + loc["saturday"]["open"]
                        + "-"
                        + loc["saturday"]["close"]
                    )
                if not loc["sunday"]["open"]:
                    sun = " Sun Closed"
                elif loc["sunday"]["open"] is None:
                    sun = " Sun Closed"
                else:
                    sun = " Sun " + loc["sunday"]["open"] + "-" + loc["sunday"]["close"]
                hours_of_operation = (
                    mon
                    + tue
                    + wed
                    + thu
                    + fri
                    + sat
                    + sun.replace("Sun 0-0", "Sun Closed")
                )
            except:

                hours_of_operation = MISSING
            if (
                hours_of_operation
                == " Mon Closed Tue Closed Wed Closed Thu Closed Fri Closed Sat Closed Sun Closed"
            ):
                hours_of_operation = MISSING
            country_code = "US"
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
