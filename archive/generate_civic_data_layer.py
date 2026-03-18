import os
import json
import requests
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "civic_data"
COUNTY_DIR = DATA_DIR / "counties"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = ROOT / "exports" / "civic_data"

for directory in [DATA_DIR, COUNTY_DIR, RAW_DIR, PROCESSED_DIR, EXPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")
BLS_API_KEY = os.getenv("BLS_API_KEY", "")

ARKANSAS_FIPS = "05"

# -----------------------------------
# Census Variables
# -----------------------------------

CENSUS_VARIABLES = {

    "population_total": "B01003_001E",
    "median_household_income": "B19013_001E",

    "poverty_total": "B17001_001E",
    "poverty_below": "B17001_002E",

    "white_alone": "B02001_002E",
    "black_alone": "B02001_003E",
    "american_indian_alone": "B02001_004E",
    "asian_alone": "B02001_005E",

    "hispanic_or_latino": "B03003_003E",

    "median_age": "B01002_001E",

    # High school age (14-17)

    "male_14": "B01001_007E",
    "male_15": "B01001_008E",
    "male_16": "B01001_009E",
    "male_17": "B01001_010E",

    "female_14": "B01001_031E",
    "female_15": "B01001_032E",
    "female_16": "B01001_033E",
    "female_17": "B01001_034E",

    # College age

    "male_18_19": "B01001_011E",
    "male_20": "B01001_012E",
    "male_21": "B01001_013E",
    "male_22_24": "B01001_014E",

    "female_18_19": "B01001_035E",
    "female_20": "B01001_036E",
    "female_21": "B01001_037E",
    "female_22_24": "B01001_038E",
}

BLS_STATE_SERIES = {
    "unemployment_rate": "LASST050000000000003"
}

# -----------------------------------
# Utility
# -----------------------------------

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def to_number(v):
    try:
        if v is None or v == "":
            return None
        if "." in str(v):
            return float(v)
        return int(v)
    except Exception:
        return None


# -----------------------------------
# Census Fetch
# -----------------------------------

def fetch_census_county_data():

    variables = ",".join(CENSUS_VARIABLES.values())

    url = (
        f"https://api.census.gov/data/2023/acs/acs5"
        f"?get=NAME,{variables}"
        f"&for=county:*"
        f"&in=state:{ARKANSAS_FIPS}"
    )

    if CENSUS_API_KEY:
        url += f"&key={CENSUS_API_KEY}"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    save_json(RAW_DIR / "census_arkansas_counties_raw.json", data)

    return data


# -----------------------------------
# Census Normalize
# -----------------------------------

def normalize_census_data(raw_rows):

    headers = raw_rows[0]
    rows = raw_rows[1:]

    normalized = []

    for row in rows:

        item = dict(zip(headers, row))

        county_name = item.get("NAME", "").replace(", Arkansas", "")
        county_fips = item.get("county")

        population = to_number(item.get(CENSUS_VARIABLES["population_total"]))

        poverty_total = to_number(item.get(CENSUS_VARIABLES["poverty_total"]))
        poverty_below = to_number(item.get(CENSUS_VARIABLES["poverty_below"]))

        poverty_rate = None

        if poverty_total and poverty_total > 0:
            poverty_rate = round((poverty_below / poverty_total) * 100, 2)

        # -----------------------------------
        # Youth Calculations
        # -----------------------------------

        high_school_age = sum([
            to_number(item.get(CENSUS_VARIABLES["male_14"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_15"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_16"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_17"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_14"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_15"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_16"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_17"])) or 0,
        ])

        high_school_seniors = (
            (to_number(item.get(CENSUS_VARIABLES["male_17"])) or 0)
            +
            (to_number(item.get(CENSUS_VARIABLES["female_17"])) or 0)
        )

        college_age = sum([
            to_number(item.get(CENSUS_VARIABLES["male_18_19"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_20"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_21"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["male_22_24"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_18_19"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_20"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_21"])) or 0,
            to_number(item.get(CENSUS_VARIABLES["female_22_24"])) or 0,
        ])

        youth_total = high_school_age + college_age

        youth_percent = None
        if population and population > 0:
            youth_percent = round((youth_total / population) * 100, 2)

        normalized_item = {

            "county_name": county_name,
            "county_fips": county_fips,
            "state_fips": item.get("state"),

            "population_total": population,
            "median_household_income": to_number(item.get(CENSUS_VARIABLES["median_household_income"])),

            "poverty_total": poverty_total,
            "poverty_below": poverty_below,
            "poverty_rate": poverty_rate,

            "high_school_age_population": high_school_age,
            "high_school_seniors_estimate": high_school_seniors,
            "college_age_population": college_age,
            "youth_population_total": youth_total,
            "youth_percent_of_population": youth_percent,

            "white_alone": to_number(item.get(CENSUS_VARIABLES["white_alone"])),
            "black_alone": to_number(item.get(CENSUS_VARIABLES["black_alone"])),
            "american_indian_alone": to_number(item.get(CENSUS_VARIABLES["american_indian_alone"])),
            "asian_alone": to_number(item.get(CENSUS_VARIABLES["asian_alone"])),
            "hispanic_or_latino": to_number(item.get(CENSUS_VARIABLES["hispanic_or_latino"])),

            "median_age": to_number(item.get(CENSUS_VARIABLES["median_age"])),

            "source": "U.S. Census ACS 5-year",
            "year": 2023
        }

        normalized.append(normalized_item)

    save_json(PROCESSED_DIR / "census_arkansas_counties_processed.json", normalized)

    return normalized


# -----------------------------------
# BLS
# -----------------------------------

def fetch_bls_state_data():

    if not BLS_API_KEY:
        return {
            "note": "No BLS API key present. Labor data not fetched.",
            "series": {}
        }

    payload = {
        "seriesid": list(BLS_STATE_SERIES.values()),
        "startyear": "2023",
        "endyear": "2024",
        "registrationkey": BLS_API_KEY
    }

    response = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    save_json(RAW_DIR / "bls_arkansas_state_raw.json", data)

    return data


def normalize_bls_state_data(raw):

    out = {
        "source": "U.S. Bureau of Labor Statistics",
        "series": {}
    }

    series_list = raw.get("Results", {}).get("series", [])

    reverse_lookup = {v: k for k, v in BLS_STATE_SERIES.items()}

    for series in series_list:

        series_id = series.get("seriesID")

        label = reverse_lookup.get(series_id, series_id)

        datapoints = []

        for item in series.get("data", []):

            datapoints.append({
                "year": item.get("year"),
                "period": item.get("period"),
                "value": item.get("value"),
                "period_name": item.get("periodName"),
            })

        out["series"][label] = {
            "series_id": series_id,
            "data": datapoints
        }

    save_json(PROCESSED_DIR / "bls_arkansas_state_processed.json", out)

    return out


# -----------------------------------
# County Files
# -----------------------------------

def build_county_files(census_data, bls_data):

    labor_note = bls_data.get("note") if isinstance(bls_data, dict) else None

    for county in census_data:

        county_fips = county["county_fips"]

        county_slug = f"{county_fips}_{county['county_name'].lower().replace(' ', '_').replace('.', '')}"

        payload = {

            "county": county,

            "labor": {
                "note": labor_note or "State-level labor seed only. County-level BLS mapping not yet added."
            },

            "youth_metrics": {
                "high_school_population": county.get("high_school_age_population"),
                "high_school_seniors": county.get("high_school_seniors_estimate"),
                "college_age_population": county.get("college_age_population"),
                "youth_population_total": county.get("youth_population_total"),
                "youth_percent": county.get("youth_percent_of_population")
            },

            "future_fields": {
                "officials": [],
                "ballot_history": [],
                "movement_examples": [],
                "chapter_links": [],
                "story_bank": []
            }
        }

        save_json(COUNTY_DIR / f"{county_slug}.json", payload)


# -----------------------------------
# State Index
# -----------------------------------

def build_state_index(census_data):

    total_population = sum([c.get("population_total") or 0 for c in census_data])

    county_index = []

    for c in census_data:

        county_index.append({
            "county_name": c["county_name"],
            "county_fips": c["county_fips"],
            "population_total": c["population_total"],
            "poverty_rate": c["poverty_rate"],
            "median_household_income": c["median_household_income"],
        })

    county_index = sorted(
        county_index,
        key=lambda x: (x["population_total"] or 0),
        reverse=True
    )

    state_payload = {

        "state": "Arkansas",
        "state_fips": ARKANSAS_FIPS,

        "generated_at": datetime.utcnow().isoformat() + "Z",

        "population_total_estimate": total_population,

        "county_count": len(census_data),

        "top_counties_by_population": county_index[:10]
    }

    save_json(EXPORT_DIR / "arkansas_state_index.json", state_payload)
    save_json(PROCESSED_DIR / "arkansas_county_index.json", county_index)


# -----------------------------------
# Metadata
# -----------------------------------

def build_metadata():

    metadata = {

        "generated_at": datetime.utcnow().isoformat() + "Z",

        "sources": {

            "census": {
                "enabled": True,
                "api_key_present": bool(CENSUS_API_KEY)
            },

            "bls": {
                "enabled": True,
                "api_key_present": bool(BLS_API_KEY)
            }
        }
    }

    save_json(EXPORT_DIR / "metadata.json", metadata)


# -----------------------------------
# Main
# -----------------------------------

def main():

    print("\n========================================")
    print(" Arkansas Civic Data Layer Generator")
    print("========================================\n")

    census_raw = fetch_census_county_data()
    census_processed = normalize_census_data(census_raw)

    bls_raw = fetch_bls_state_data()
    bls_processed = normalize_bls_state_data(bls_raw) if "series" not in bls_raw else bls_raw

    build_county_files(census_processed, bls_processed)

    build_state_index(census_processed)

    build_metadata()

    print("\nData layer complete.\n")


if __name__ == "__main__":
    main()