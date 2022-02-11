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

    url = "https://www.loanmaxtitleloans.net/SiteMap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")
    linklist.append(
        "https://www.loanmaxtitleloans.net/locations/wisconsin/green-bay/704-s-military-ave"
    )
    linklist.append(
        "https://www.loanmaxtitleloans.net/locations/arizona/mesa/2009-w-main-st"
    )
    for link in linklist:
        try:
            link = link.text
        except:
            pass
        try:
            if (
                "locations" in link
                and len(link.split("locations/", 1)[1].split("/")) > 2
            ):
                pass
            else:
                continue
        except:
            continue
        print(link)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        pcode = soup.find("span", {"itemprop": "postalCode"}).text
        title = "Loanmax - " + city + ", " + state
        phone = soup.find("span", {"itemprop": "telephone"}).text
        hours = soup.find("div", {"class": "store_hours"}).text.replace("\n", " ")

        yield SgRecord(
            locator_domain="https://www.loanmaxtitleloans.net/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
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
