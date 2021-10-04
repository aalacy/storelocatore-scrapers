from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape import sgpostal as parser
import json
import re

session = SgRequests()
website = "emetabolic_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.emetabolic.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        for i in range(1, 52):
            p = str(i)
            url = "https://www.emetabolic.com/?maps_markers=" + p
            r = session.get(url, headers=headers)
            response = r.text
            loclist = response.split('"markers":')[1].split("]}", 1)[0]
            loclist = loclist + "]"
            loclist = json.loads(loclist)
            if loclist:
                for loc in loclist:
                    title = loc["name"].strip()
                    lat = loc["lat"].strip()
                    longt = loc["lng"]
                    link_url = loc["link_url"]
                    if link_url.find("emetabolic.com") == -1:
                        link_url = "https://www.emetabolic.com/" + link_url
                    try:
                        res = session.get(link_url, headers=headers)
                        soup = BeautifulSoup(res.text, "html.parser")
                        div = soup.findAll("div", {"class": "location-contact-data"})
                        if len(div) > 0:
                            add = div[0].text
                            add = re.sub(pattern, ",", add)
                            add = add.rstrip(" Get Directions,")
                            add = add.replace(",", "")
                        div = soup.findAll("div", {"class": "location-contact-data"})
                        if (len(div)) == 0:
                            phone = "<MISSING>"
                        else:
                            phone = div[1].text
                            phone = phone.strip()

                        time = soup.findAll("div", {"class": "location-hours-info"})
                        HOO = ""
                        for day in time:
                            hours = day.text
                            HOO = HOO + hours
                        if HOO == "":
                            HOO = "<MISSING>"
                        HOO = HOO.strip()

                    except AttributeError:
                        add = loc["address"]
                        add = add.replace(",", "")
                        phone = "<MISSING>"
                        HOO = "<MISSING>"

                    parsed = parser.parse_address_usa(add)
                    street1 = (
                        parsed.street_address_1
                        if parsed.street_address_1
                        else "<MISSING>"
                    )
                    street = (
                        (street1 + ", " + parsed.street_address_2)
                        if parsed.street_address_2
                        else street1
                    )
                    city = parsed.city if parsed.city else "<MISSING>"
                    state = parsed.state if parsed.state else "<MISSING>"
                    pcode = parsed.postcode if parsed.postcode else "<MISSING>"

                    if street == "15060 Sequoia Pkwy # 6Tigard":
                        street = "15060 Sequoia Pkwy # 6"
                        city = "Tigard"

                    if state.find("Usa") != -1:
                        state = state.split()[0]

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=link_url,
                        location_name=title.strip(),
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=pcode.strip(),
                        country_code="US",
                        store_number=SgRecord.MISSING,
                        phone=phone.strip(),
                        location_type=SgRecord.MISSING,
                        latitude=lat,
                        longitude=longt,
                        hours_of_operation=HOO.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
