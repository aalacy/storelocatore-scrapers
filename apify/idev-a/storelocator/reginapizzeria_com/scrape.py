from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

locator_domain = "http://reginapizzeria.com/"
base_url = "http://reginapizzeria.com/"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .replace("\t", "")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def _phone(val):
    return val.replace("-", "").isdigit()


def addy_ext(addy):
    address = addy.split(",")
    if len(address) == 1:
        state_zip = address[0].strip().split(" ")
        city = state_zip[0]
        state = state_zip[1]
        zip_code = "<MISSING>"
    else:
        city = address[0]
        state_zip = address[1].strip().split(" ")

        state = state_zip[0]
        zip_code = state_zip[1]

    return city, state, zip_code


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        locations = soup.select("div.dropdown-menu a.dropdown-item")
        for link in locations:
            page_url = locator_domain + link["href"]
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            addy = [_ for _ in soup1.select_one("div.mbr-article").stripped_strings]
            location_type = "<MISSING>"
            if "temporarily closed" in addy[0]:
                location_type = "Closed"
                del addy[0]
            if "Regina Pizz" in addy[0]:
                del addy[0]

            location_name = " ".join(
                [_ for _ in soup1.select_one("h3.mbr-header__text").stripped_strings]
            )
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])

            hours_of_operation = ""
            if soup1.select(
                "div.mbr-section__container--last div.mbr-article--wysiwyg p"
            ):
                hours_of_operation = "; ".join(
                    [
                        _
                        for _ in soup1.select(
                            "div.mbr-section__container--last div.mbr-article--wysiwyg p"
                        )[-1].stripped_strings
                    ]
                )
            phone = ""
            if "Open" in addy[2]:
                phone = addy[3].replace("Telephone number:", "").strip()
            elif len(addy) >= 5:
                phone = addy[2]
            if not _phone(phone):
                phone = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_valid1(location_name),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation=_valid1(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
