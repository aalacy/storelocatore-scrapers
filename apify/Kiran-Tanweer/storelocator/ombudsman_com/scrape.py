import re
import json
import usaddress
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ombudsman_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def fetch_data():
    url = "https://www.ombudsman.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.select("a[href*=state]")
    for st in statelist:
        stlink = st["href"]
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        if r.url == "https://az.ombudsman.com/locations/":
            loclist = r.text.split('<script type="application/ld+json">')[1:]
            phone_list = soup.findAll("div", {"class": "cl-lgmap_location-list-item"})
            for loc, temp in zip(loclist, phone_list):
                temp = temp.get_text(separator="|", strip=True).split("|")
                phone = temp[-1]
                if "Fax:" in phone:
                    phone = temp[-2]
                loc = json.loads(loc.split("</script>")[0])
                location_name = loc["name"]
                page_url = loc["url"]
                log.info(page_url)
                address = loc["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                latitude = loc["geo"]["latitude"]
                longitude = loc["geo"]["longitude"]
                yield SgRecord(
                    locator_domain="https://www.ombudsman.com/",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

        else:
            loclist = soup.findAll("div", {"class": "location-group"})
            coordlist = (
                "["
                + r.text.split("mapp.data.push( ", 1)[1]
                .split("[", 1)[1]
                .split("]", 1)[0]
                + "]"
            )
            coordlist = json.loads(coordlist)
            for loc in loclist:
                divlist = loc.findAll("li")
                for div in divlist:
                    try:
                        link = div.find("h4").find("a")["href"]
                        link = stlink.replace("/locations/", "") + link
                    except:
                        link = stlink
                    log.info(link)
                    div = div.get_text(separator="|", strip=True).split("|")
                    if len(div) > 3:
                        if re.match(
                            r"^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$", div[3]
                        ):
                            phone = div[3]
                        else:
                            phone = SgRecord.MISSING
                    else:
                        phone = SgRecord.MISSING
                    location_name = div[0]
                    address = div[1] + " " + div[2]
                    address = address.replace(",", " ")
                    address = usaddress.parse(address)
                    i = 0
                    street_address = ""
                    city = ""
                    state = ""
                    zip_postal = ""
                    while i < len(address):
                        temp = address[i]
                        if (
                            temp[1].find("Address") != -1
                            or temp[1].find("Street") != -1
                            or temp[1].find("Recipient") != -1
                            or temp[1].find("Occupancy") != -1
                            or temp[1].find("BuildingName") != -1
                            or temp[1].find("USPSBoxType") != -1
                            or temp[1].find("USPSBoxID") != -1
                        ):
                            street_address = street_address + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            zip_postal = zip_postal + " " + temp[0]
                        i += 1
                    for coord in coordlist:
                        if (
                            coord["title"] == location_name
                            or "Campus" in coord["title"]
                        ):
                            lat = coord["point"]["lat"]
                            longt = coord["point"]["lng"]
                            break
                    location_name = location_name.encode("ascii", "ignore").decode(
                        "ascii"
                    )
                    yield SgRecord(
                        locator_domain="https://www.ombudsman.com/",
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.replace(",", "").strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
