from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    titlelist = []
    url = "https://southstatebank.com/Global/About/CRA/Locations-Listing"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=location-detail]")

    p = 0
    for link in linklist:
        if "https://southstatebank.com/" in link["href"]:
            link = link["href"]
        else:
            link = "https://southstatebank.com" + link["href"]
        if link in titlelist:
            continue
        titlelist.append(link)
        r = session.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip()
        street = soup.find("div", {"class": "address"}).findAll("p")[0].text
        city, state = (
            soup.find("div", {"class": "address"}).findAll("p")[1].text.split(", ", 1)
        )
        state, pcode = state.split(" ", 1)
        hours = (
            soup.text.split("Location Hours", 1)[1]
            .split("Drive Up ATM", 1)[0]
            .replace("\n", " ")
            .strip()
        )
        phone = soup.find("div", {"class": "contact"}).findAll("a")[1].text
        lat = (
            soup.find("div", {"class": "detail-map"})["data-initdata"]
            .split('"Lat":', 1)[1]
            .split(",", 1)[0]
        )
        longt = (
            soup.find("div", {"class": "detail-map"})["data-initdata"]
            .split('"Lng":', 1)[1]
            .split("}", 1)[0]
        )
        if "Branch Features" in soup.text:
            ltype = "Branch | ATM"
        else:
            ltype = "ATM"
        try:
            hours = hours.split("Walk Up ATM", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Branch Features", 1)[0]
        except:
            pass
        if hours:
            hours = (
                hours.split("Drive Thru")[0]
                .replace("Lobby  By Appointment Only", "")
                .replace("Lobby", "")
                .strip()
            )
        street = city
        city = state.replace(",", "")
        state, pcode = pcode.split(" ", 1)
        if len(state) > 3:
            city = city + " " + state.replace(",", "")
            state, pcode = pcode.split(" ", 1)
        if pcode.isdigit():
            pass
        else:
            city = city + " " + state
            state, pcode = pcode.split(" ", 1)
        if len(state) > 3:
            city = city + " " + state.replace(",", "")
            state, pcode = pcode.split(" ", 1)
        store = link.split("/")[-2]
        sgw.write_row(
            SgRecord(
                page_url=link,
                location_name=title,
                street_address=street,
                city=city.replace(",", ""),
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=store,
                phone=phone,
                location_type=ltype,
                latitude=lat,
                longitude=longt,
                locator_domain="https://southstatebank.com/",
                hours_of_operation=hours,
                raw_address="<MISSING>",
            )
        )
        p += 1


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        fetch_data(writer)


scrape()
