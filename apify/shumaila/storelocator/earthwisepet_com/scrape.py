from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    url = "https://earthwisepet.com/wp-admin/admin-ajax.php"
    dataobj = {"action": "get_all_stores", "lat": "", "lng": ""}
    loclist = session.post(url, data=dataobj, headers=headers).json()
    for loc in loclist:
        loc = loclist[loc]
        store = loc["ID"]
        title = loc["na"]

        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["st"]
        pcode = loc["zp"]
        try:
            city = loc["ct"].strip()
        except:
            city = "<MISSING>"
        ccode = loc["co"]
        state = loc["rg"]
        try:
            phone = loc["te"].strip()
        except:
            phone = "<MISSING>"
        hours = "<MISSING>"
        try:
            link = loc["we"]
            if "search" not in link:
                link = link + link.split("://", 1)[1].split(".", 1)[0]
                link = link.replace(".com", ".com/").replace(".com//", ".com/").lower()

                try:

                    r = session.get(link, headers=headers)

                    soup = BeautifulSoup(r.text, "html.parser")
                    hours = (
                        soup.find("div", {"class": "store-info-body"})
                        .text.replace("The Store is open on :", "")
                        .replace("\n", " ")
                        .strip()
                    )

                    try:
                        hours = hours.split(street.split(" ", 1)[0], 1)[0]
                    except:
                        pass
                except:
                    hours = "<MISSING>"
        except:
            link = "<MISSING>"
        yield SgRecord(
            locator_domain="https://earthwisepet.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
