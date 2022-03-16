from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.novacare.com"
base_url = "https://www.novacare.com//sxa/search/results/?s={D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}|{CC39E325-A49A-4785-B763-C515E5679B4D}&itemid={891FD4CE-DCBE-4AA5-8A9C-539DF5FCDE97}&sig=&autoFireSearch=true&v=%7B80D13F78-0C6F-42A0-A462-291DD2D8FA17%7D&p=5000"


def determine_brand(x):
    brands = {
        "Banner Physical Therapy": "https://resources.selectmedical.com/logos/op/Banner-PT-logo.png",
        "Emory Rehabilitation Outpatient Center": "https://resources.selectmedical.com/logos/op/Emory-Rehab-OP.png",
        "POSI - Prosthetic Orthotic Solutions International": "https://resources.selectmedical.com/logos/op/POSI-signage.png",
        "Kessler Rehabilitation Center": "https://resources.selectmedical.com/logos/op/OP_Kessler-Rehabilitation-Center.png",
        "PennState Health Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/PennState-Health-logo.png",
        "NovaCareKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/NovaCareKids-logo.png",
        "Kort": "https://resources.selectmedical.com/logos/op/brand-kort(1).png",
        "SSMHealth": "https://resources.selectmedical.com/logos/op/OP_SSMHealth-DayInstitute.png",
        "BaylorScott & White - Institute for Rehabilitaiton": "https://resources.selectmedical.com/logos/op/Baylor-Scott-White-logo.png",
        "NovaCare - Ohio Health": "https://resources.selectmedical.com/logos/op/OhioHealth-logo.png",
        "Physio": "https://resources.selectmedical.com/logos/op/Physio-Logo_MR-Small.png",
        "RushKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/RUSHKids-logo.png",
        "SelectKIDS Pediatric Therapy": "https://resources.selectmedical.com/logos/op/SelectKids-logo.png",
        "SACO BAY Orthopaedic & Sports": "https://resources.selectmedical.com/logos/op/SacoBay-4cLogoNoTag.png",
        "NovaCare Rehabilitation (wellspan)": "https://resources.selectmedical.com/logos/op/OP_wellspan-logo.png",
        "UnityPoint Health Marshalltown": "https://resources.selectmedical.com/logos/op/UnityPoint-Health-Marshalltown-logo.png",
        "CRI": "https://resources.selectmedical.com/logos/op/CRI-logo.png",
        "NovaCare Prostetics & Orthotics": "https://resources.selectmedical.com/logos/op/OP_NovaCare-PO-logo.png",
        "SSM Health Physical Therapy": "https://resources.selectmedical.com/logos/op/OP_SSMHealth-Physical-Therapy.png",
        "PennState Hereshey Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/REHAB_PennState-Rehabilitation-Hospital---USE-THIS-IN-THE-SCROLL.png",
        "West Gables Rehabilitation Hospital": "https://resources.selectmedical.com/logos/op/REHAB_West-Gables-Rehab-Hosp.png",
        "LifeBridge Health": "https://resources.selectmedical.com/logos/op/OP_NovaCare-LifeBridge.png",
        "Select Physical Therapy": "https://resources.selectmedical.com/logos/op/OP_Select-Physical-Therapy---USE-THIS-ONE-ON-THE-SCROLL.png https://resources.selectmedical.com/logos/op/SPT-Cedars-Sinai-logo.png",
        "Banner CHILDREN'S Physical Therapy": "https://resources.selectmedical.com/logos/op/BannerChildrensPT-logo.png",
        "Rehab ASSOCIATES": "https://resources.selectmedical.com/logos/op/RehabAssociates-logo.png",
        "SSM Health Day Institute": "https://resources.selectmedical.com/logos/op/SSM-Health-Day-Institute.png",
        "RUSH Physical Therapy": "https://resources.selectmedical.com/logos/op/RUSHPT-logo.png",
        "NovaCare Rehabilitation": "https://resources.selectmedical.com/logos/op/brand-novacare.png",
        "CSM - Champion Sports Medicine": "https://resources.selectmedical.com/logos/op/ChampionSportsMed-logo.png",
        "GRANDVIEW HEALTH": "https://resources.selectmedical.com/logos/op/Champion-Grandview-logo.png",
        "Concorde Therapy Group": "https://resources.selectmedical.com/logos/op/Concorde-logo.png",
        "HealthWorks Rehab & Fitness": "https://resources.selectmedical.com/logos/op/HealthWorks-logo.png",
        "Dignity Health Physical Therapy": "https://resources.selectmedical.com/logos/op/DignityHealth-PT-logo.png",
    }
    for brand, link in brands.items():
        if x in link:
            return brand

    try:
        x = x.split("/")[-1].split(".")[0].split("-logo")[0]
        return x
    except Exception:
        pass
    return "<MISSING>"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Results"]

        for _ in locations:
            loc = bs(_["Html"], "lxml")
            addr = list(
                loc.select_one("div.loc-result-card-address-container").stripped_strings
            )
            hours = [
                " ".join(tr.stripped_strings)
                for tr in loc.select("div.field-businesshours table tr")
            ]
            location_type = determine_brand(loc.img["src"])
            yield SgRecord(
                page_url=loc.a["href"],
                store_number=_["Id"],
                location_name=loc.select_one("div.loc-result-card-name").text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=loc.select_one(
                    "div.loc-result-card-phone-container"
                ).text.strip(),
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
