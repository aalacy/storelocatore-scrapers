from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    session = SgRequests()

    url = "https://www.temptingplaces.com/fr/page/decouvrez-notre-collection-unique-de-boutique-hotels-temptingplaces.2708.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    clist = {
        "espagne": "ES",
        "france": "FR",
        "portugal": "PT",
        "inde": "IN",
        "maroc": "MA",
        "madagascar": "MR",
        "sainte": "LC",
        "les": "PW",
        "italie": "IT",
        "grece": "GR",
        "indonesie": "ID",
        "sri": "LK",
        "maldives": "MV",
        "israel": "IL",
    }
    linklist = soup.findAll("h3", {"class": "item-suptitle"})
    for link in linklist:
        link = link.find("a")["href"]
        try:
            link = link.split("#backlink", 1)[0]
        except:
            pass
        session = SgRequests()
        r = session.get(link, headers=headers)
        r.encoding = "utf-8-sig"
        content = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script>", 1
        )[0]

        content = json.loads(content)

        try:
            phone = content["telephone"][0]
        except:
            phone = "<MISSING>"
        street = content["address"]["streetAddress"]
        city = content["address"]["addressLocality"]
        pcode = content["address"]["postalCode"]
        title = content["name"]
        lat = r.text.split("&quot;lat&quot;:&quot;", 1)[1].split("&quot;", 1)[0]
        longt = r.text.split("&quot;lng&quot;:&quot;", 1)[1].split("&quot;", 1)[0]
        ccode = link.split("fr/page/", 1)[1].split("/", 1)[1].split("-", 1)[0]
        ccode = clist[ccode]
        title = (
            title.encode("utf-8")
            .decode("utf-8")
            .replace("Ã³", "ó")
            .replace("Â´", "´")
            .replace(
                "Ã",
                "à",
            )
        )
        yield SgRecord(
            locator_domain="https://www.temptingplaces.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.strip(),
            country_code=ccode,
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
