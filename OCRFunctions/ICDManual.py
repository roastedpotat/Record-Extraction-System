import re

def closest(lst, K):
    if not lst:
        return None
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def find_primary_icd(records):
    for record in records:
        split = record.split("Provisional Diagnosis")
        if len(split)<2:
            split = record.split("Primary ICD")

        pattern = r"[A-Z]\d{1,3}\.?\d*"

        icd_code = list(re.finditer(pattern, split[1], re.IGNORECASE))
        primary = re.search(pattern=r"Yes", string= split[1], flags=re.IGNORECASE)
        if not primary:
            yield None
        lowest = primary.span()[0]
        list_icd = []

        for icd in icd_code:
            if icd.span()[1] < lowest:
                list_icd.append(icd.span()[1])
        num = closest(list_icd, lowest)
        for p_icd in icd_code:
            if p_icd.span()[1] == num:
                yield p_icd.group()
