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
    statelist = [
        "AL",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NJ",
        "NM",
        "NY",
        "NC",
        "OH",
        "OK",
        "OR",
        "PA",
        "SC",
        "TN",
        "TX",
        "UT",
        "VA",
        "WA",
        "WI",
    ]
    url = "https://huntingtonhelps.com/location/state-list"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "centerListing"})
    for state in statelist:
        subdivlist = divlist.find("div", {"id": state})
        location = subdivlist.findAll("div", {"class": "listing__item"})
        for loc in location:
            title = loc.find("h3").text
            address = loc.findAll("div", {"class": "address"})
            street = address[0].text
            address2 = address[1].text
            city, address2 = address2.split(",")
            city = city.lstrip()
            city = city.rstrip()
            address2 = address2.lstrip()
            address2 = address2.rstrip()
            state, zipcode = address2.split(" ")
            state = state.lstrip()
            state = state.rstrip()
            zipcode = zipcode.lstrip()
            zipcode = zipcode.rstrip()
            phone = loc.find("div", {"class": "phone"}).text
            loclink = loc.find("h3").find("a")["href"]
            loclink = "https://huntingtonhelps.com" + loclink
            link = session.get(loclink, headers=headers)
            soup = BeautifulSoup(link.text, "html.parser")
            hour = soup.find("div", {"class": "hours col-sm-6"})
            li = hour.findAll("li")
            hours = ""
            for ele in li:
                hr = ele.text
                hours = hours + " " + hr
            hours = hours.lstrip()
            hours = hours.rstrip()
            try:
                longt, lat = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d", 1)
                )
            except:
                lat = longt = "<MISSING>"
            yield SgRecord(
                locator_domain="https://huntingtonhelps.com/",
                page_url=loclink,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zipcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
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
