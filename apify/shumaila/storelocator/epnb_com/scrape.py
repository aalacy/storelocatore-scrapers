from bs4 import BeautifulSoup
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

    url = "https://www.epnb.com/about-enb/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Branch Details")')
    for link in linklist:
        link = link["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").text.strip().replace(" Branch Office", "")
        street = soup.find("div", {"class": "street-address"}).text
        city, state = soup.find("div", {"class": "city-state-zip"}).text.split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        ltype = soup.find("div", {"class": "location-atm"}).text
        if "ATM Available" in ltype:
            ltype = "Branch|ATM"
        else:
            ltype = "Branch"
        phone = soup.find("div", {"class": "phone-number"}).find("a").text
        try:

            lat = soup.find("div", {"class": "marker"})["data-lat"]
            longt = soup.find("div", {"class": "marker"})["data-lng"]
        except:
            lat = longt = "<MISSING>"
        try:
            hours = soup.find("div", {"class": "location-hours"}).text
            hourlist = hours.replace("\xa0", " ").strip().split("Day:")[1:]

            if "Drive-Up" in title:
                hours = ""
                for hr in hourlist:

                    try:
                        hours = (
                            hours
                            + hr.split("Drive", 1)[0]
                            + " "
                            + hr.split("Drive", 1)[1].split("Hours:", 1)[1].strip()
                            + " "
                        )
                    except:
                        hours = "<MISSING>"
            else:
                hours = ""
                for hr in hourlist:

                    try:
                        hours = (
                            hours
                            + hr.split("Lobby", 1)[0]
                            + " "
                            + hr.split("Lobby Hours:", 1)[1]
                            .split("Drive", 1)[0]
                            .strip()
                            + " "
                        )
                    except:
                        hours = "<MISSING>"
        except:
            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.epnb.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
