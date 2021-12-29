import re
from bs4 import BeautifulSoup
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }

    base_url = "https://www.hueymagoos.com"
    p_url = "https://hueymagoos.com/locations/"
    r = session.get(p_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    pattern = re.compile(r"\s\s+")
    data_list = soup.findAll("div", {"class": "loc-box-new"})

    for loc in data_list:
        try:
            title = loc.find("h3").text
        except:
            continue
        details = loc.find("p")
        phone = ""
        address = ""
        details = str(details).replace("<br/>", "\n")
        details = BeautifulSoup(details, "html.parser")

        if len(details.findAll("a")) > 1:

            if details.findAll("a")[0].get("href").find("tel") != -1:
                phone = details.findAll("a")[0].text
            else:
                phone = "<MISSING>"
            if details.findAll("a")[1].get("href").find("maps") != -1:
                address = re.sub(pattern, "\n", details.findAll("a")[1].text).strip()
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            else:
                address = "<MISSING>"
            hours_of_operation = (
                details.findAll("a")[1].next_sibling.lstrip().replace("–", "-")
            )
        elif len(details.findAll("a")) == 1:

            if details.findAll("a")[0].get("href").find("tel") != -1:
                phone = details.findAll("a")[0].text
            else:
                phone = "<MISSING>"
            if details.findAll("a")[0].get("href").find("maps") != -1:
                address = re.sub(pattern, "\n", details.findAll("a")[0].text).strip()
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
            else:
                address = "<MISSING>"
            if details.findAll("a")[0].next_sibling.find("am") or details.findAll("a")[
                0
            ].next_sibling.find("pm"):
                hours_of_operation = (
                    details.findAll("a")[0]
                    .next_sibling.lstrip()
                    .replace("–", "-")
                    .replace("\n", " ")
                )
            else:
                hours_of_operation = "<MISSING>"
        else:

            if details.text:
                address = details.text
                street = address.split("\n")[0]
                city = address.split("\n")[1].split(", ")[0].strip()
                state = address.split("\n")[1].split(", ")[1].split(" ")[0].strip()
                zip = address.split("\n")[1].split(", ")[1].split(" ")[1]
                phone = SgRecord.MISSING
                hours_of_operation = SgRecord.MISSING
            else:

                details = loc.findAll("p")[-1].text.split("\n")
                city, state = details[-1].split(", ", 1)
                state, zip = state.split(" ", 1)
                street = " ".join(details[0 : len(details) - 1]).strip()

                phone = SgRecord.MISSING
                hours_of_operation = "Opening Soon"
        if len(phone) < 2:
            phone = "<MISSING>"
        yield SgRecord(
            locator_domain=base_url,
            page_url=p_url,
            location_name=title,
            street_address=street.replace(",", "").replace("#", "No."),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip,
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation.replace("\n", " "),
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
