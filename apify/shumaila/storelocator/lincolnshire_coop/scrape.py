from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.lincolnshire.coop/storefinder"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "map-panel"})
    for div in divlist:
        lat = div["data-latitude"]
        longt = div["data-longitude"]
        ltype = div["data-category"]
        title = div["data-title"]
        store = div["data-id"]
        link = "https://www.lincolnshire.coop" + div["data-url"]
        address = div["data-address"]
        pcode = address.split(",")[-1].strip()
        city = address.split(",")[-2].strip()
        state = "<MISSING>"
        ccode = "GB"
        street = address.split(",")
        street = " ".join(street[0 : len(street) - 2])
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        phone = r.text.split('"telephone": "', 1)[1].split('"', 1)[0]
        hourslist = r.text.split('"openingHoursSpecification": ', 1)[1].split(
            "</script>", 1
        )[0]
        hourslist = hourslist + "]"
        hourslist = re.sub(pattern, "", hourslist).strip().replace("}]}]", "}]")
        hourslist = json.loads(hourslist)
        hours = ""
        for hr in hourslist:
            try:
                hours = hr["dayOfWeek"] + " " + hr["opens"] + " - " + hr["closes"] + " "
            except:
                pass
        yield SgRecord(
            locator_domain="https://www.lincolnshire.coop/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=str(ltype),
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
