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
    url = "https://api.zoeskitchen.com/customer-api/customer-stores/summary-by-state"
    divlist = session.get(url, headers=headers, verify=False).json()
    for div in divlist:
        loclist = divlist[div]
        for loc in loclist:
            title = loc["name"]
            store = loc["storeNumber"]
            street = loc["address"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"]
            link = (
                "https://zoeskitchen.com/locations/store/"
                + state.lower()
                + "/"
                + loc["urlFriendlyName"]
            )
            page = session.get(link, headers=headers, verify=False)
            soup1 = BeautifulSoup(page.text, "html.parser")
            try:
                hourlist = soup1.find("table", {"class": "hours"})
                hourlist = soup1.findAll("tr")
                hours = ""
                for hourd in hourlist:
                    hour = hourd.text
                    hour = hour.replace("\n", "")
                    hours = hours + hour + " "
            except:
                hours = "<MISSING>"
            try:
                phone = soup1.find("a", {"class": "tel"}).text
            except:
                phone = "<MISSING>"
            lat = page.text.split("lat: ", 1)[1].split(",", 1)[0]
            longt = page.text.split("lng: ", 1)[1].split(" }", 1)[0]

            hours = hours.rstrip()

            yield SgRecord(
                locator_domain="https://zoeskitchen.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=store,
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
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
