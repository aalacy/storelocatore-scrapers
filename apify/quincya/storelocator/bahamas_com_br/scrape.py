import re
import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "http://www.bahamas.com.br/ListaLojas.aspx"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"

    locator_domain = "https://www.bahamas.com.br"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(locator_domain)
    time.sleep(2)
    driver.find_element_by_id("ddlCidade").find_elements_by_tag_name("option")[
        1
    ].click()
    time.sleep(2)
    driver.get(base_link)
    time.sleep(2)
    driver.find_element_by_id(
        "ctl00_ContentPlaceHolder1_ddlCidadeFiltro"
    ).find_elements_by_tag_name("option")[1].click()
    time.sleep(2)
    driver.find_element_by_id(
        "ctl00_ContentPlaceHolder1_ibtnFiltroBandeiraBuscar"
    ).click()
    time.sleep(2)

    base = BeautifulSoup(driver.page_source, "lxml")
    items = base.find_all(class_="loja")

    for item in items:
        location_name = item.find(class_="titulo").text.strip()
        raw_address = item.find(
            "span",
            {"id": re.compile(r"ctl00_ContentPlaceHolder1_rptLoja_ctl[0-9].+_lblEnd")},
        ).text.split("-")
        street_address = " ".join(raw_address[:-2]).strip()
        city = raw_address[-2].split("(")[0].strip()
        state = raw_address[-1].strip()
        zip_code = item.find(
            "span",
            {"id": re.compile(r"ctl00_ContentPlaceHolder1_rptLoja_ctl[0-9].+_lblCep")},
        ).text.strip()
        country_code = "BR"
        store_number = item["num"]
        location_type = ""
        phone = item.find(
            "span",
            {
                "id": re.compile(
                    r"ctl00_ContentPlaceHolder1_rptLoja_ctl[0-9].+_lblTelefone"
                )
            },
        ).text.strip()
        hours_of_operation = (
            item.find(
                "span",
                {
                    "id": re.compile(
                        r"ctl00_ContentPlaceHolder1_rptLoja_ctl[0-9].+_lblHorario"
                    )
                },
            )
            .text.strip()
            .replace("\n", " ")
        )
        latitude = ""
        longitude = ""
        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=item.find(
                    "span",
                    {
                        "id": re.compile(
                            r"ctl00_ContentPlaceHolder1_rptLoja_ctl[0-9].+_lblEnd"
                        )
                    },
                ).text.strip(),
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
