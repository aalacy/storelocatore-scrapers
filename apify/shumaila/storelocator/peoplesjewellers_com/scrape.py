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
    url = "https://www.peoplesjewellers.com/store-finder/view-all-states"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.select("a[href*=view-stores]")

    for slink in state_list:
        slink = "https://www.peoplesjewellers.com/store-finder/" + slink["href"]

        r = session.get(slink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        branchlist = soup.find("div", {"class": "view-all-stores"}).findAll(
            "div", {"class": "col-lg-3"}
        )

        for branch in branchlist:
            try:
                link = branch.find("a")["href"]
                title = branch.find("a").text
            except:
                continue
            if branch.find("a")["href"].find("/null") == -1:

                link = "https://www.peoplesjewellers.com" + branch.find("a")["href"]

                r = session.get(link, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.find("h1", {"itemprop": "name"}).text
                street = soup.find("span", {"itemprop": "streetAddress"}).text
                city = soup.find("span", {"itemprop": "addressLocality"}).text
                state = soup.find("span", {"itemprop": "addressRegion"}).text
                pcode = soup.find("span", {"itemprop": "postalCode"}).text
                ccode = soup.find("span", {"itemprop": "addressCountry"}).text
                phone = soup.find("span", {"itemprop": "telephone"}).text
                coord = soup.find("a", {"class": "link-directions"})["href"]
                lat, longt = coord.split("Location/")[1].split(",", 1)
                store = link.split("-peo")[1]
                hours = (
                    str(soup)
                    .split('"openings":', 1)[1]
                    .split("{", 1)[1]
                    .split("}", 1)[0]
                    .replace('"', "")
                    .replace(":", " ")
                )
                hours = re.sub(pattern, " ", hours).strip()
            else:

                street = branch.find("span", {"itemprop": "streetAddress"}).text
                city = branch.find("span", {"itemprop": "addressLocality"}).text
                state = branch.find("span", {"itemprop": "addressRegion"}).text
                pcode = branch.find("span", {"itemprop": "postalCode"}).text
                phone = branch.find("span", {"itemprop": "telephone"}).text

                store = "<MISSING>"
                ccode = "CA"
                lat = "<MISSING>"
                longt = "<MISSING>"
                hours = "<MISSING>"
                link = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.peoplesjewellers.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=store,
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
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
