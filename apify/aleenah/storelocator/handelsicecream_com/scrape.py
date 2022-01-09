from bs4 import BeautifulSoup
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

    weeklist = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    url = "https://handelsicecream.com"
    r = session.get(url, headers=headers)
    loclist = r.text.split("var branches = ", 1)[1].split("</script", 1)[0]
    loclist = json.loads(loclist.replace("};", "}").strip())
    for loc in loclist:
        loc = loclist[loc]
        store = loc["location"]
        title = loc["title"]
        address = loc["address"]
        street = address.split("<", 1)[0]
        city = address.split(">", 1)[1]
        city, state = city.split(", ", 1)
        pcode = state.strip().split(" ")[-1]
        state = state.replace(pcode, "").strip()

        lat = loc["lat"]
        longt = loc["lng"]
        link = loc["link"]

        hours = ""
        for day in weeklist:
            hours = hours + day + " " + loc[day] + " "
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            phone = soup.find("div", {"class": "phone"}).text
        except:
            phone = "<MISSING>"
        yield SgRecord(
            locator_domain=url,
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
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
