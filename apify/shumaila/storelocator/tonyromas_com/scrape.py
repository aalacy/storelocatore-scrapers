from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


MISSING = SgRecord.MISSING


def fetch_data():

    url = "https://tonyromas.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("a[href*=address]")
    for div in divlist:

        divlink = div["href"]
        ccode = divlink.split("country=", 1)[1]
        divlink = divlink.replace("&per_page=5", "&per_page=25")
        r = session.get(divlink, headers=headers)
        try:
            soup = BeautifulSoup(r.text, "html.parser")
        except:
            continue
        loclist = soup.find("ul", {"class": "posts-list-wrapper"}).findAll("li")

        for loc in loclist:
            try:
                if "single-post" in loc["id"]:
                    address = loc.find("span", {"class": "address"}).text
                    title = loc.find("h2").text.strip()
                    link = loc.find("h2").find("a")["href"]

                    r = session.get(link, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    address = soup.find("div", {"class": "ad1"}).text.strip()

                    try:
                        phone = soup.select_one("a[href*=tel]").text.strip()
                    except:
                        phone = "<MISSING>"
                    try:
                        hours = (
                            loc.find("ul", {"class": "gmw-hours-of-operation"})
                            .text.replace("pm", "pm ")
                            .replace("losed", "losed ")
                        )
                    except:
                        hours = "<MISSING>"
                    try:
                        coord = soup.findAll("iframe")[1]["src"]
                        r = session.get(coord, headers=headers)
                        lat, longt = (
                            r.text.split('",null,[null,null,', 1)[1]
                            .split("]", 1)[0]
                            .split(",", 1)
                        )
                    except:
                        continue
                    ltype = "<MISSING>"
                    if "Temporarily Closed" in title:
                        ltype = "Temporarily Closed"
                    elif "COMING SOON" in title:
                        ltype = "COMING SOON"
                    raw_address = address
                    raw_address = raw_address.replace("\n", " ").strip()

                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    pcode = zip_postal.strip() if zip_postal else MISSING

                    yield SgRecord(
                        locator_domain="https://tonyromas.com/",
                        page_url=link,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=pcode.strip(),
                        country_code=ccode,
                        store_number=SgRecord.MISSING,
                        phone=phone.strip(),
                        location_type=ltype,
                        latitude=str(lat),
                        longitude=str(longt),
                        hours_of_operation=hours,
                        raw_address=raw_address.replace("\n", " ").strip(),
                    )
            except:
                continue


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
