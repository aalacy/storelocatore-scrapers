from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xa0\\xa", " ")
        .replace("\\xae", "")
    )


def addy_ext(addy):
    address = addy.split(",")
    state_zip = address[1].strip().split(" ")
    return addy.split(",")[0], state_zip[0], state_zip[-1]


def _phone(phone):
    return phone.replace("-", "").isdigit()


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.claros.com/"
        base_url = "https://www.claros.com/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.findAll("a", href=re.compile("contact-"))
        for _ in locations:
            if "-us" in _["href"]:
                continue
            page_url = f"{locator_domain}{_['href']}"
            r = session.get(page_url)
            location_name = f"Claro's {_.text}"
            street_address = ""
            city = ""
            state = ""
            phone = ""
            zip_postal = ""
            location_soup = bs(r.text, "lxml")
            text_blocks = [
                _valid(bb.text)
                for bb in location_soup.findAll("span")
                if bb.text.strip()
            ]
            hours = []
            for block in text_blocks:
                if block.startswith("Meet our"):
                    _x = text_blocks.index(block)
                    street_address = text_blocks[_x - 2]
                    city, state, zip_postal = addy_ext(text_blocks[_x - 1])
                    idx = _x
                    while True:
                        if idx == len(text_blocks) or text_blocks[idx] in [
                            "Covina",
                            "La Habra",
                            "Upland",
                            "Tustin",
                            "Announcements",
                            "Six Locations to Serve You!",
                        ]:
                            break
                        if phone and text_blocks[idx] not in hours:
                            hours.append(text_blocks[idx])

                        if _phone(text_blocks[idx]):
                            phone = text_blocks[idx]
                        idx += 1
                    hours_of_operation = "; ".join(hours).replace("Open ", "")

                    break

            latitude = (
                str(location_soup)
                .split("{ zoom:")[1]
                .split("}, key,")[0]
                .replace(" 14, lat: ", "")
                .replace("lng:", "")
                .split(",")[0]
                .strip()
            )
            longitude = (
                str(location_soup)
                .split("{ zoom:")[1]
                .split("}, key,")[0]
                .replace(" 14, lat: ", "")
                .replace("lng:", "")
                .split(",")[1]
                .strip()
            )

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
