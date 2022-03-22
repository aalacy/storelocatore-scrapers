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

    url = "https://www.bobbienoonans.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    stlist = soup.select("a[href*=locations]")[1:]
    for st in stlist:
        stlink = st["href"]
        if "locations/" not in stlink:
            continue
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.find("div", {"class": "entry-content"}).findAll(
            "div", {"class": "one-half"}
        )
        for div in divlist:

            try:
                if "http" not in div.find("a")["href"]:
                    link = "https://www.bobbienoonans.com" + div.find("a")["href"]
                else:
                    link = div.find("a")["href"]
            except:
                continue
            title = div.find("a").text

            content = div.text.strip().splitlines()

            m = 1
            try:
                street = content[m]
                m = m + 1
            except:
                continue
            pcode = ""
            try:
                city, state = content[m].split(", ", 1)
                state, pcode = state.split(" ", 1)
            except:

                m = m + 1

                try:
                    city, state = content[m].split(", ", 1)
                    state, pcode = state.split(" ", 1)
                except:
                    city, pcode = content[m].split(" IL ", 1)
                    state = "IL"
                m = m + 1
            m = m + 3
            hours = content[m]
            if "a.m." not in hours:
                hours = "<MISSING>"
            phone = div.text.split("P: ", 1)[1].split("\n", 1)[0]

            yield SgRecord(
                locator_domain=url,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=str(state),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
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
