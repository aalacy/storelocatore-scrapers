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

    url = "https://www.habitat.org/volunteer/near-you/find-your-local-habitat"
    page = session.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find(
        "select",
        {"class": "form-select--white form-select chosen-disable form-item__text"},
    )
    repo_list = maindiv.findAll("option")
    for n in range(1, len(repo_list)):
        repo = repo_list[n]
        stlink = "https://www.habitat.org" + repo["value"]
        page = session.get(stlink, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.findAll("article", {"class": "address-listing"})
        for card in maindiv:
            title = card.text
            link = "https://www.habitat.org" + card.find("a")["href"]
            page = session.get(link, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")
            store = page.text.split('"id":"map', 1)[1].split('"', 1)[0]
            lat = page.text.split('{"lat":', 1)[1].split(",", 1)[0]
            longt = page.text.split(',"lng":', 1)[1].split("}", 1)[0]
            street = soup.find("span", {"class": "address-line1"}).text
            city = soup.find("span", {"class": "locality"}).text
            state = soup.find("span", {"class": "administrative-area"}).text
            pcode = soup.find("span", {"class": "postal-code"}).text
            phone = str(soup.find("div", {"class": "card__phone"}))
            try:
                phone = (
                    phone.split("</svg>", 1)[1]
                    .split("</div>", 1)[0]
                    .replace("\n", "")
                    .strip()
                )
            except:
                phone = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.habitat.org",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
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
