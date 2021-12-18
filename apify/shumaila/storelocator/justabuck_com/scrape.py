from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headers1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.justabuck.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    divlist = soup.findAll("loc")

    for div in divlist:
        link = div.text
        try:
            if len(link.split("Find-A-Store", 1)[1]) > 4:
                pass
            else:
                continue
        except:
            continue
        store = "<MISSING>"

        plink = (
            "https://www.justabuck.com/Home/GetPartialview?id=1025&url="
            + link.split("/")[-1]
            + "&n=1"
        )

        headers1["referer"] = link
        r = session.post(plink, headers=headers1)
        soup = BeautifulSoup(r.text, "html.parser")
        coord = soup.find("iframe")["src"]
        soup = re.sub(cleanr, "\n", str(soup)).strip()
        soup = re.sub(pattern, "\n", str(soup)).strip()
        title = soup.split("\n")[0]
        street = soup.split("\n")[2]
        city, state = soup.split("\n")[3].split(", ", 1)
        state, pcode = state.split(" ", 1)

        phone = soup.split("Phone:", 1)[1].split("\n", 1)[1].split("\n", 1)[0].strip()
        hours = soup.split("Store Hours", 1)[1].split("Back To", 1)[0].strip()
        hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()

        if "OPENING SOON" in hours:
            continue
        r = session.get(coord, headers=headers)
        try:
            lat, longt = (
                r.text.split('",null,[null,null,', 1)[1].split("]", 1)[0].split(",")
            )
        except:

            lat, longt = (
                r.text.split(",[[[")[2].split(",", 1)[1].split("]", 1)[0].split(",")
            )
        yield SgRecord(
            locator_domain="https://www.justabuck.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=store,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace("\r", " ").replace("\x96", "").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()


scrape()
