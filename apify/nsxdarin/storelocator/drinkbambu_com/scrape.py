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

    url = "https://www.drinkbambu.com/find-bambu/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "wpv-addon-maps-marker"})

    for div in divlist:

        lat = div["data-markerlon"]
        longt = div["data-markerlat"]
        title = div.find("h3").text
        phone = div.findAll("p")[1].text
        link = (
            "https://www.drinkbambu.com" + div.find("a", {"class": "view-loc"})["href"]
        )

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        street = soup.find("span", {"itemprop": "address"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text.replace(
            ", Canada", ""
        )
        pcode = soup.find("span", {"itemprop": "postalCode"}).text
        ltype = "<MISSING>"
        try:
            hours = soup.find("p", {"class": "hours"}).text.replace("\n", " ").strip()
        except:
            if "Coming Soon" in soup.text:
                ltype = "Coming Soon"
            hours = "<MISSING>"
        ccode = "US"
        if pcode.isdigit():
            pass
        else:
            ccode = "CA"
        yield SgRecord(
            locator_domain="https://www.drinkbambu.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
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
