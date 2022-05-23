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

    url = "https://www.cmxcinemas.com/Location/GetCinemaLocations"
    webdata = session.get(url, headers=headers)
    webdata = BeautifulSoup(webdata.text, "html.parser")
    statelist = webdata.find("select", {"id": "drpStateloc"}).findAll("option")
    for state in statelist:
        if state.text == "Select your state":
            continue
        loclist = session.get(
            "https://www.cmxcinemas.com/Locations/FilterLocations?state="
            + state.text
            + "&city=&searchText="
        )
        loclist = json.loads(loclist.text)
        loclist = loclist["listloc"]
        for loc in loclist:
            if loc["totalcities"] == "0":
                pass
            else:
                citylist = loc["city"]
                state = loc["state"]
                for city in citylist:
                    title = city["cinemaname"]
                    if title == "CMX Odyssey IMAX":
                        street = city["address"].split(",")[0]
                    else:
                        street = city["address"]
                    pcode = city["postalcode"]
                    cityn = city["locCity"]
                    link = (
                        "https://www.cmxcinemas.com/Locationdetail/" + city["slugname"]
                    )

                    r = session.get(link, headers=headers)
                    try:
                        longt, lat = (
                            r.text.split("!2d", 1)[1].split("!2m", 1)[0].split("!3d")
                        )
                    except:
                        lat = "<MISSING>"
                        longt = "<MISSING>"
                    try:
                        phone = r.text.split("Contact Us: ")[1].split("</p>")[0]
                    except:
                        try:
                            phone = r.text.split("Contact us: ", 1)[1].split("\n", 1)[0]
                        except:
                            phone = "<MISSING>"
                    try:
                        phone = phone.split("\n", 1)[0].replace('"', "")
                    except:
                        pass
                    yield SgRecord(
                        locator_domain="https://www.cmxcinemas.com",
                        page_url=link,
                        location_name=title,
                        street_address=street.strip(),
                        city=cityn.rstrip(" " + state),
                        state=state.strip(),
                        zip_postal=pcode.strip(),
                        country_code="US",
                        store_number=SgRecord.MISSING,
                        phone=phone.strip(),
                        location_type=SgRecord.MISSING,
                        latitude=str(lat),
                        longitude=str(longt),
                        hours_of_operation=SgRecord.MISSING,
                    )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
