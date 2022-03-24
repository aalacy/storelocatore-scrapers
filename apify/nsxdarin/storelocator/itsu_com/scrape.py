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

    url = "https://www.itsu.com/wp-content/uploads/geojson/open_sesame_geo.json"
    loclist = session.get(url, headers=headers).json()["features"]
    for loc in loclist:

        lat = loc["geometry"]["coordinates"][0]
        longt = loc["geometry"]["coordinates"][0]
        store = loc["properties"]["post-id"]
        title = loc["properties"]["title"]
        content = loc["properties"]["content"]
        content = BeautifulSoup(content, "html.parser")
        link = content.find("a")["href"]
        title = content.find("div", {"class": "stockist-title"}).text

        address = content.findAll("div", {"class": "stockist-address"})[-1].text

        address = address.split(", ")
        pcode = address[-1]
        city = address[-2]
        street = " ".join(address[0 : len(address) - 3])
        try:
            phone = content.find("span", {"class": "highlight"}).text
        except:
            phone = "<MISSING>"
        ltype = "<MISSING>"
        if "opening soon" in title:
            ltype = "Opening Soon"
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = soup.find("ul", {"id": "hours"}).text.replace("pm", "pm ")
        try:
            hours = hours.split("half", 1)[0]
        except:
            pass
        yield SgRecord(
            locator_domain="https://www.itsu.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.strip(),
            country_code="GB",
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
