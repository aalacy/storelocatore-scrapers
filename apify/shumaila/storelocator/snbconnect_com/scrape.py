from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://snbconnect.com/Locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("table", {"class": "Table-Staff-3Column"}).findAll("td")
    for state in statelist:
        link = state.find("a", {"class": "Button2"})["href"]
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

                phone = str(loc[2])

                street = loc[0]
                try:
                    city, state = loc[1].split(", ", 1)
                    state, pcode = state.strip().split(" ", 1)
                except:
                    street = street = " " + loc[1]
                    city, state = loc[2].split(", ", 1)
                    state, pcode = state.strip().split(" ", 1)
                    phone = loc[3]
                hours = (
                    loc1.lower()
                    .split("lobby\xa0hours", 1)[1]
                    .split("drive", 1)[0]
                    .replace("\n", " ")
                    .strip()
                )
                hours = hours.replace(
                    "(by appointment 9:00am-10:00am; 3:00pm-5:30pm)", ""
                ).strip()
                yield SgRecord(
                    locator_domain="https://snbconnect.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=SgRecord.MISSING,
                    phone=phone.replace(".", "").strip(),
                    location_type="Branch | ATM",
                    latitude=SgRecord.MISSING,
                    longitude="<MISSING>",
                    hours_of_operation=hours,
                )
        except:

            loclist = soup.text.split("LOCATIONS AND HOURS", 1)[1]
            loclist = re.sub(pattern, "\n", loclist).strip().split("Meet your bankers")

            for loc in loclist:

                try:
                    loc = loc.split("COUNCIL BLUFFS", 1)[1]
                    loc = "COUNCIL BLUFFS" + loc
                except:
                    pass
                loc = loc.strip().splitlines()

                title = loc[0]
                address = loc[1].split(", ")
                try:
                    hours = (
                        loc[2]
                        .replace("\n", " ")
                        .lower()
                        .split("lobby", 1)[1]
                        .split("drive", 1)[0]
                        .replace("\n", " ")
                        .strip()
                    )
                except:
                    continue
                state = address[-1]
                city = address[-2]
                street = " ".join(address[0 : len(address) - 2])
                state, pcode = state.split(" ", 1)
                try:
                    pcode, phone = pcode.strip().split(" ", 1)
                except:
                    phone = pcode[5:]
                    pcode = pcode[0:5]
                try:
                    hours = hours.split(":", 1)[1]
                except:
                    pass
                yield SgRecord(
                    locator_domain="https://snbconnect.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=SgRecord.MISSING,
                    phone=phone.replace(".", "").strip(),
                    location_type="Branch | ATM",
                    latitude=SgRecord.MISSING,
                    longitude="<MISSING>",
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

            m = 0
            title = "SECURITY NATIONAL BANK OF TEXAS"
            try:
                phone = loc[m].split(" at ", 1)[1]
            except:
                m = m + 1
                phone = loc[m].split(" at ", 1)[1]
            m = m + 1
            hours = loc[1]
            m = m + 1
            address = loc[m].split(", ")

            state = address[-1]
            city = address[-2]
            street = " ".join(address[0 : len(address) - 2])
            state, pcode = state.lstrip().split(" ", 1)

            yield SgRecord(
                locator_domain="https://snbconnect.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.replace(".", "").strip(),
                location_type="Branch | ATM",
                latitude=SgRecord.MISSING,
                longitude="<MISSING>",
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
