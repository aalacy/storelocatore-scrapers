from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data():

    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    base_url = "https://www.dfs-banken.nl/"
    r = session.get("https://www.dfs-banken.nl/content/winkel", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("main", {"id": "storeDetailsPage"}).findAll("section")
    for div in divlist:
        title = div.find("h1").text.strip()
        raw_address = div.find("p")
        raw_address = re.sub(cleanr, "\n", str(raw_address))
        raw_address = re.sub(pattern, "\n", str(raw_address))
        raw_address1 = raw_address.replace("\n", " ").strip()
        raw_address = raw_address.strip().splitlines()
        city = raw_address[-1]
        pcode = raw_address[1].replace(",", "")
        street = raw_address[0]

        try:
            temp = " "
            if len(city.split(",")) == 2:
                pcode = city.split(",", 1)[0]
                city = city.split(",", 1)[1]
            elif len(city.split(",")) == 3:
                pcode = city.split(",")[0]
                temp = city.split(",")[1]
                city = city.split(",")[2]
            street = " ".join(raw_address[0 : len(raw_address) - 1]) + " " + temp
        except:
            pass
        phone = div.find("p", {"class": "phoneDetails"}).text.split(" ", 1)[1]
        hours = div.find("ol").text
        hours = re.sub(pattern, " ", str(hours)).strip()
        longt, lat = (
            div.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d", 1)
        )
        try:
            lat = lat.split("!", 1)[0]
        except:
            pass
        store = (
            div.find("a", {"class": "apptBtn"})["href"]
            .split("location/", 1)[1]
            .split("/", 1)[0]
        )

        state = "<MISSING>"
        hours = hours.encode("ascii", "ignore").decode("ascii")
        yield SgRecord(
            locator_domain=base_url,
            page_url="https://www.dfs-banken.nl/content/winkel",
            location_name=title,
            street_address=street.replace("Ekkersrijt Ekkersrijt", "Ekkersrijt"),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code="NL",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace(" â€¦", "").strip(),
            raw_address=raw_address1,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=5,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
