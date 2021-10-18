from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.ombudsman.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.select("a[href*=state]")
    for st in statelist:
        stlink = st["href"]
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location-group"})
        coordlist = (
            "["
            + r.text.split("mapp.data.push( ", 1)[1].split("[", 1)[1].split("]", 1)[0]
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
                content = re.sub(cleanr, "\n", str(div)).strip()
                content = re.sub(pattern, "\n", str(content)).strip()

                if (
                    "(" in content.splitlines()[-1]
                    or ")" in content.splitlines()[-1]
                    or "-" in content.splitlines()[-1]
                ):
                    title = content.split("\n", 1)[0]
                    phone = content.splitlines()[-1]
                    pcode = content.splitlines()[-2]
                    state = content.splitlines()[-3]
                    city = content.splitlines()[-4]
                    title = content.splitlines()[0]
                    street = (
                        content.split(title, 1)[1]
                        .split(city + "\n", 1)[0]
                        .replace("\n", " ")
                        .strip()
                    )
                else:
                    if "Learn" in content:
                        content = content.split("Learn", 1)[0]
                    content = content.splitlines()
                    title = content[0]
                    street = content[1]
                    try:
                        state = content[2].strip().split(" ")[-2]
                        city = content[2].split(" " + state, 1)[0]
                        pcode = content[2].split(state + " ", 1)[1]
                    except:
                        city = content[-2]
                        state, pcode = content[-1].split(" ", 1)
                    phone = "<MISSING>"
                lat = longt = "<MISSING>"
                for coord in coordlist:
                    if coord["title"] == title or "Campus" in coord["title"]:
                        lat = coord["point"]["lat"]
                        longt = coord["point"]["lng"]
                        break
                title = title.encode("ascii", "ignore").decode("ascii")
                yield SgRecord(
                    locator_domain="https://www.ombudsman.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.replace(",", "").strip(),
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
