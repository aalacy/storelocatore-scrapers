import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "snbconnect_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://snbconnect.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://snbconnect.com/Locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("table", {"class": "Table-Staff-3Column"}).findAll("td")
    for state in statelist:
        link = state.find("a", {"class": "Button2"})["href"]
        log.info(link)
        state = state.find("h2").text
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("table", {"class": "Expandable"})
        try:

            for i in range(0, len(loclist)):
                title = loclist[i].find("h4").text
                loc = str(
                    loclist[i]
                    .find("table", {"class": "Table-Staff-2Column"})
                    .find("td")
                )

                loc = re.sub(cleanr, "\n", loc)
                loc1 = re.sub(pattern, "\n", loc).strip()
                loc = loc1.splitlines()
                street = loc[0]
                city, state = loc[1].split(", ", 1)
                state, pcode = state.strip().split(" ", 1)
                phone = loc[2]
                hours = (
                    loc1.lower()
                    .split("lobby hours", 1)[1]
                    .split("drive", 1)[0]
                    .replace("\n", " ")
                    .strip()
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=title,
                    street_address=street,
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours,
                )
        except:
            loclist = soup.text.split("LOCATIONS AND HOURS", 1)[1]
            loclist = re.sub(pattern, "\n", loclist).strip().split("VISIT MY SITE")
            for loc in loclist:

                loc = loc.strip().splitlines()
                title = loc[0]
                if "Find us on the map!" in title:
                    continue
                address = loc[1].split(", ")
                hours = (
                    loc[2]
                    .replace("\n", " ")
                    .lower()
                    .split("lobby hours", 1)[1]
                    .split("drive", 1)[0]
                    .replace("\n", " ")
                    .strip()
                )

                state = address[-1]
                city = address[-2]
                street = " ".join(address[0 : len(address) - 2])
                state, pcode = state.split(" ", 1)
                try:
                    pcode, phone = pcode.strip().split(" ", 1)
                except:
                    phone = pcode[5:]
                    pcode = pcode[0:5]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=title,
                    street_address=street,
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours,
                )

        if len(loclist) == 0:
            loclist = soup.text.split("Location and Hours", 1)[1]
            loc = (
                re.sub(pattern, "\n", loclist)
                .strip()
                .split("24 HOUR ATM", 1)[0]
                .splitlines()
            )
            phone = loc[0].split(" at ", 1)[1]
            hours = loc[1]
            address = loc[2].split(", ")
            state = address[-1]
            city = address[-2]
            street = " ".join(address[0 : len(address) - 2])
            state, pcode = state.lstrip().split(" ", 1)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title,
                street_address=street,
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours,
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
