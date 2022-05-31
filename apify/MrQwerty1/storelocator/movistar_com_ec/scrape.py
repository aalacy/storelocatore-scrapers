from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_states():
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@id='proviSelect']/option[not(@value)]/text()")


def get_params():
    pars = set()
    states = get_states()
    params = {
        "p_p_id": "com_vass_movistar_ec_cavs_web_INSTANCE_JQOwwHsrZMqZ",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_cacheability": "cacheLevelPage",
    }

    for state in states:
        data = {
            "provi": state.replace(" ", "+"),
            "search": "Canton",
        }

        r = session.post(page_url, headers=headers, params=params, data=data)
        cities = r.text.replace("[", "").replace("]", "").split(", ")
        for j in cities:
            pars.add((state, j))

    return pars


def fetch_data(sgw: SgWriter):
    pars = get_params()

    params = {
        "p_p_id": "com_vass_movistar_ec_cavs_web_INSTANCE_JQOwwHsrZMqZ",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_cacheability": "cacheLevelPage",
    }

    for state, city in pars:
        data = {
            "search": "CAVS",
            "provi": state.replace(" ", "+"),
            "cant": city.replace(" ", "+"),
        }
        r = session.post(page_url, headers=headers, params=params, data=data)
        try:
            js = r.json()
        except:
            js = []

        for j in js:
            street_address = j.get("address")
            country_code = "EC"
            location_name = j.get("name")

            geo = j.get("geoRef") or ""
            geo = geo.replace(", ", "!").replace(",", ".")
            if "!-" in geo:
                latitude = geo.split("!-")[0].strip()
                longitude = "-" + geo.split("!-")[1].strip()
            elif ".-" in geo:
                latitude = geo.split(".-")[0].strip()
                longitude = "-" + geo.split(".-")[1].strip()
            else:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            if longitude.count(".") > 1:
                longitude = ".".join(longitude.split(".")[:2])
            if longitude.count("-") > 1:
                longitude = longitude.replace("--", "-")

            _tmp = []
            source = j.get("schedule") or "<html>"
            root = html.fromstring(source)
            line = root.xpath("//text()")
            line = list(
                filter(None, [li.replace("Horarios:", "").strip() for li in line])
            )
            if len(line) % 2 == 1:
                _tmp.append(" ".join(line).replace("\r\n", ""))
            else:
                for day, inter in zip(line[::2], line[1::2]):
                    _tmp.append(f"{day} {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.movistar.com.ec/"
    page_url = "https://www.movistar.com.ec/centros-de-atencion"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.movistar.com.ec/centros-de-atencion",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.movistar.com.ec",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
