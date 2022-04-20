from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MISSING = SgRecord.MISSING


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.casaley.com.mx/index.php/nuestra-organizacion/nuestras-tiendas.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("table")

    for div in divlist:
        rowlist = div.findAll("tr")
        for row in rowlist:
            loclist = row.findAll("td")
            for loc in loclist:
                ltype = loc.find("img")
                loc = re.sub(cleanr, "\n", str(loc))
                loc = re.sub(pattern, "\n", str(loc)).strip()

                try:
                    title = loc.splitlines()[0]
                except:
                    continue
                check = ""
                if len(title) < 4:
                    title = loc.splitlines()[0] + " " + loc.splitlines()[1]
                    check = loc.splitlines()[1]
                ltype = ltype["alt"].replace("logo ", "")
                flag = 0
                store = ""
                try:
                    store = title.split("(", 1)[1].split(")", 1)[0].strip()
                    flag = 1
                except:
                    if loc.splitlines()[1].replace("(", "").replace(")", "").isdigit():
                        store = (
                            loc.splitlines()[1]
                            .replace("(", "")
                            .replace(")", "")
                            .strip()
                        )
                        flag = 2
                    else:
                        "<MISSING>"
                phone = loc.splitlines()[-1]
                if "Horario" in phone:
                    hours = phone.replace("Horario: ", "")
                    phone = loc.splitlines()[-2]

                    if "(" not in phone:
                        phone = loc.splitlines()[-3]
                        if len(phone) < 6:
                            phone = loc.splitlines()[-3] + " " + loc.splitlines()[-2]
                else:
                    hours = "<MISSING>"
                if "(" not in phone:
                    phone = loc.splitlines()[-2]
                try:
                    phone = phone.split(".", 1)[1]
                except:
                    pass
                try:
                    phone = phone.split(":", 1)[1]
                except:
                    pass
                try:
                    phone = phone.split(",", 1)[0]
                except:
                    pass
                if (
                    phone.replace("(", "")
                    .replace(")", "")
                    .replace("-", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    flag = 1
                    pass
                else:
                    phone = "<MISSING>"
                try:
                    phone = phone.split("(", 1)[1]
                    phone = "(" + phone
                except:
                    pass
                if len(phone.split(" ")) > 2 and len(phone.split(" ")[1]) > 4:

                    phone = " ".join(phone.split(" ")[0:2])
                address = ""

                if check == "":
                    check = title
                if flag == 1:
                    address = (
                        loc.split(check, 1)[1]
                        .split("\n", 1)[1]
                        .split(phone, 1)[0]
                        .replace("\n", " ")
                        .strip()
                    )
                    flag = 0
                elif flag == 2:
                    address = (
                        loc.split(store, 1)[1]
                        .split("\n", 1)[1]
                        .split(phone, 1)[0]
                        .replace("\n", " ")
                        .strip()
                    )
                    flag = 0
                elif "<MISSING>" in phone:
                    address = loc.split(check, 1)[1].replace("\n", " ").strip()
                address = (
                    address.replace(" Tel.", "")
                    .replace(" TEL.", "")
                    .replace(" TEL:", "")
                    .replace(" tel:", "")
                )

                title = title.replace("P LAZ", "PLAZ").strip()
                raw_address = address
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                pcode = zip_postal.strip() if zip_postal else MISSING

                pcode = (
                    pcode.replace("CP.", "")
                    .replace("C.P.:", "")
                    .replace("C.P.", "")
                    .replace("C P ", "")
                    .replace("CP ")
                    .strip()
                )
                try:
                    hours = hours.split("o: ", 1)[1]
                except:
                    pass
                if len(store) < 2:
                    store = "<MISSING>"
                yield SgRecord(
                    locator_domain="https://www.casaley.com.mx/",
                    page_url=url,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state,
                    zip_postal=pcode.strip(),
                    country_code="MX",
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type=ltype,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours,
                    raw_address=address,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
