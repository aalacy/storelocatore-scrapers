import re

GLOBAL_PATTERN = {
    "denmark": r"\d{4}",
    "faroe Islands": r"\d{3}",
    "finland": r"\d{5}",
    "faroe islands": r"\d{3}",
    "iceland": r"\d{3}",
    "lithuania": r"\d{5}",
    "netherlands": r"\d{4}[ ]?[A-Z]{2}",
    "norway": r"\d{4}",
    "sweden": r"\d{3}[ ]?\d{2}",
    "ireland": r"^(A|[C-F]|H|K|N|P|R|T|[V-Y])([0-9])([0-9]|W)( )?([0-9]|A|[C-F]|H|K|N|P|R|T|[V-Y]){4}",
    "united kingdom": r"GIR[ ]?0AA|((AB|AL|B|BA|BB|BD|BH|BL|BN|BR|BS|BT|CA|CB|CF|CH|CM|CO|CR|CT|CV|CW|DA|DD|DE|DG|DH|DL|DN|DT|DY|E|EC|EH|EN|EX|FK|FY|G|GL|GY|GU|HA|HD|HG|HP|HR|HS|HU|HX|IG|IM|IP|IV|JE|KA|KT|KW|KY|L|LA|LD|LE|LL|LN|LS|LU|M|ME|MK|ML|N|NE|NG|NN|NP|NR|NW|OL|OX|PA|PE|PH|PL|PO|PR|RG|RH|RM|S|SA|SE|SG|SK|SL|SM|SN|SO|SP|SR|SS|ST|SW|SY|TA|TD|TF|TN|TQ|TR|TS|TW|UB|W|WA|WC|WD|WF|WN|WR|WS|WV|YO|ZE)(\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}))|BFPO[ ]?\d{1,4}",
}


def global_zip_code(country_code, string):
    keyword = country_code.lower()
    if keyword in GLOBAL_PATTERN:
        zip_code = re.match(GLOBAL_PATTERN[keyword], string)
        if re.match(GLOBAL_PATTERN[keyword], string):
            return zip_code.group()
    return False
