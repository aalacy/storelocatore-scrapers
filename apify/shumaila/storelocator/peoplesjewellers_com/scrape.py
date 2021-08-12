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


def fetch_data():

    url = "https://www.peoplesjewellers.com/store-finder/view-all-states"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.find("div", {"id": "0"}).findAll("a")

    for slink in state_list:
        slink = "https://www.peoplesjewellers.com/store-finder/" + slink["href"]

        r = session.get(slink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        branchlist = soup.findAll("div", {"class": "viewstoreslist"})

        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        for branch in branchlist:

            if branch.find("a")["href"].find("/null") == -1:
                link = "https://www.peoplesjewellers.com" + branch.find("a")["href"]

                r = session.get(link, headers=headers, verify=False)
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
                soup = str(soup)
                hours = (
                    soup.split('detailSectionHeadline">Hours</div>')[1]
                    .split("{", 1)[1]
                    .split("}", 1)[0]
                )
                hours = hours.replace('"', "").replace("\n", " ").replace("::", " ")
                hours = re.sub(pattern, " ", hours).lstrip()
            else:
                det = re.sub(cleanr, "\n", str(branch))
                det = re.sub(pattern, "\n", det).splitlines()

                i = 1
                title = det[i]
                i = i + 1
                street = det[i]
                i = i + 1
                state = ""
                try:
                    city, state = det[i].split(", ", 1)
                except:
                    street = street + " " + det[i]
                    i = i + 1

                    try:
                        city, state = det[i].split(", ", 1)
                    except:
                        city, state = det[-2].split(", ", 1)
                state, pcode = state.lstrip().replace("\xa0", " ").split(" ", 1)

                i = i + 1
                try:
                    phone = det[i]
                except:
                    phone = "<MISSING>"
                store = "<MISSING>"
                ccode = "CA"
                lat = "<MISSING>"
                longt = "<MISSING>"
                hours = "<MISSING>"
                link = "<MISSING>"
            if len(pcode.replace(" ", "")) > 7:
                temp, pcode = pcode.split(" ", 1)
                state = state + " " + temp
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
