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

    url = "https://www.campbowwow.com/locations/?CallAjax=GetLocations"
    loclist = session.get(url, headers=headers).json()

    for loc in loclist:

        ltype = "<MISSING>"
        link = "https://www.campbowwow.com" + loc["Path"]
        store = loc["FranchiseLocationID"]
        title = loc["FranchiseLocationName"]
        street = loc["Address1"] + loc["Address2"]
        city = loc["City"]
        state = loc["State"]
        pcode = loc["ZipCode"]
        ccode = loc["Country"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        phone = loc["Phone"]

        if loc["ComingSoon"] == 0:
            pass
        else:
            ltype = "Coming Soon"
        if len(str(phone)) > 3:
            if "-" not in phone:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        else:
            phone = "<MISSING>"
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = (
                soup.find("ul", {"class": "hours-block"})
                .text.replace("\n", " ")
                .strip()
            )
            try:
                hours = hours.split(" See", 1)[0]
            except:
                pass
        except:
            hours = "<MISSING>"
            ltype = "Coming Soon"
        yield SgRecord(
            locator_domain="https://www.campbowwow.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
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
