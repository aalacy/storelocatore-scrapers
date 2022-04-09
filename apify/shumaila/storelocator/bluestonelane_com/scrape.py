from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://bluestonelane.com/cafe-and-coffee-shop-locations/?shop-sort=nearest&view-all=1&lat=&lng="
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "homebox-address"})
    linklist = []
    for div in divlist:
        link = div["href"]

        if link in linklist:
            continue
        linklist.append(link)
        r = session.get(link, headers=headers)
        ccode = "US"
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip()
        street = soup.find("span", {"id": "yext-address"})
        try:
            store = street["data-yext-location-id"]
        except:

            store = "<MISSING>"
            continue
        url = (
            "https://knowledgetags.yextpages.net/embed?key=6Af24AhHWVK9u_N4dzlSiNnLaAoxr-dpa-xe7Zf76O9rU3Eb4m0xxX6-7A_CxoZF&account_id=6868880511088594204&location_id="
            + store
        )

        r = session.get(url, headers=headers)
        address = r.text.split('"address":{', 1)[1].split("},", 1)[0]
        address = "{" + address + "}"
        address = json.loads(address)
        street = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        pcode = address["postalCode"]
        geo = r.text.split('"geo":', 1)[1].split("},", 1)[0]
        geo = geo + "}"
        geo = json.loads(geo)
        lat = geo["latitude"]
        longt = geo["longitude"]
        try:
            hourslist = r.text.split('"openingHoursSpecification":', 1)[1].split(
                "}],", 1
            )[0]
            hourslist = hourslist + "}]"
            hourslist = json.loads(hourslist)
            hours = ""

            for hr in hourslist:
                try:
                    day = hr["dayOfWeek"]
                except:
                    continue
                try:
                    opens = hr["opens"]
                except:
                    hours = hours + day + " " + "Closed"
                    continue
                closes = hr["closes"]
                cltime = (int)(closes.split(":", 1)[0])
                if cltime > 12:
                    cltime = cltime - 12
                hours = (
                    hours
                    + day
                    + " "
                    + opens
                    + " AM - "
                    + str(cltime)
                    + ":"
                    + closes.split(":", 1)[1]
                    + " PM "
                )
        except:

            hours = "<MISSING>"
        if len(hours.split("Closed")) > 4:
            hours = "Temporarily Closed"
        phone = r.text.split('"telephone":"', 1)[1].split('"', 1)[0].replace("+1", "")
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        ccode = "US"

        if pcode.isdigit():
            pass
        elif "-" in pcode:
            ccode = "GB"
        else:
            ccode = "CA"
        yield SgRecord(
            locator_domain="https://bluestonelane.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
