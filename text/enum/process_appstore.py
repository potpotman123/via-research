#!/usr/bin/env python3
"""Process appstore CSV to map apps to transit agencies."""

import csv
import re
from pathlib import Path

def extract_agency_info(name, bundle_id, description):
    """Extract agency information from app data."""

    if not description:
        description = ""

    desc_lower = description.lower()
    name_lower = name.lower()
    bundle_lower = bundle_id.lower() if bundle_id else ""

    # Initialize results
    agency = ""
    agency_type = "unknown"
    city = ""
    state = ""
    country = ""
    program_name = name
    confidence = "low"
    notes = ""

    # === INTERNATIONAL SERVICES ===

    intl_patterns = [
        (r"dubai", "Road and Transport Authority", "transit_agency", "Dubai", "", "United Arab Emirates", "high"),
        (r"abu dhabi", "", "private", "", "", "United Arab Emirates", "high"),
        (r"ajman", "", "private", "", "", "United Arab Emirates", "high"),
        (r"bc transit", "BC Transit", "transit_agency", "", "BC", "Canada", "high"),
        (r"boka resa|sl ", "SL", "transit_agency", "Stockholm", "", "Sweden", "high"),
        (r"clicbus|atac", "ATAC", "transit_agency", "Rome", "", "Italy", "high"),
        (r"electromin", "", "private", "", "", "Saudi Arabia", "medium"),
        (r"busplus", "", "private", "", "", "France", "medium"),
        (r"connect2.*north lincs", "", "private", "", "", "United Kingdom", "medium"),
        (r"easy tad|tad", "", "private", "", "", "France", "medium"),
    ]

    for pattern, agency_name, atype, c, s, ctry, conf in intl_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, ctry, program_name, conf, notes

    # === VIA'S OWN SERVICES ===

    via_own_patterns = [
        r"via driver",
        r"^downtowner$",
        r"field trips",
        r"shuttle - powered by via",
        r"^shuttle$",
    ]

    for pattern in via_own_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return "", "via_own", "", "", "", program_name, "high", notes

    # === US SERVICES ===

    country = "US"  # Default for US services

    # University services
    university_patterns = [
        (r"marquette", "Marquette University", "university", "Milwaukee", "WI"),
        (r"columbia", "Columbia University", "university", "New York", "NY"),
        (r"(osu|oregon state).*corvallis|corvallis.*osu", "Oregon State University", "university", "Corvallis", "OR"),
        (r"east carolina|ecu ride", "East Carolina University", "university", "Greenville", "NC"),
        (r"fsu|florida state", "Florida State University", "university", "Tallahassee", "FL"),
        (r"harvard|evening van", "Harvard University", "university", "Cambridge", "MA"),
        (r"umass|massachusetts", "University of Massachusetts", "university", "Amherst", "MA"),
        (r"michigan state|msu", "Michigan State University", "university", "East Lansing", "MI"),
        (r"cornell", "Cornell University", "university", "Ithaca", "NY"),
        (r"northwestern", "Northwestern University", "university", "Evanston", "IL"),
        (r"nyu|new york university", "New York University", "university", "New York", "NY"),
        (r"uc davis|ucdavis", "University of California Davis", "university", "Davis", "CA"),
        (r"utd|ut dallas", "University of Texas at Dallas", "university", "Richardson", "TX"),
    ]

    for pattern, agency_name, atype, c, s in university_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, country, program_name, "high", notes

    # Transit agencies and cities from name and description patterns
    agency_patterns = [
        # Name patterns -> (agency, type, city, state)
        (r"arlington transportation|city of arlington", "City of Arlington", "city", "Arlington", "TX"),
        (r"antelope valley transit|avta", "Antelope Valley Transit Authority", "transit_agency", "Lancaster", "CA"),
        (r"chattanooga|carta go", "Chattanooga Area Regional Transportation Authority", "transit_agency", "Chattanooga", "TN"),
        (r"sarasota|breeze", "Sarasota County Area Transit", "transit_agency", "Sarasota", "FL"),
        (r"chandler flex", "City of Chandler", "city", "Chandler", "AZ"),
        (r"calexico", "City of Calexico", "city", "Calexico", "CA"),
        (r"carts now|bastrop", "Bastrop County Ride Service", "transit_agency", "Bastrop", "TX"),
        (r"traverse city|bata link|grand traverse", "Traverse City Area Ride Service", "transit_agency", "Traverse City", "MI"),
        (r"bay transit express|gloucester", "Virginia Department of Transportation", "state_dot", "Gloucester", "VA"),
        (r"bayview shuttle|sfmta", "San Francisco Municipal Transportation Agency", "transit_agency", "San Francisco", "CA"),
        (r"bcrta|butler county", "Butler County Regional Transit Authority", "transit_agency", "Butler County", "OH"),
        (r"bft connect|richland", "Ben Franklin Transit", "transit_agency", "Richland", "WA"),
        (r"bolt|brighton, co", "City of Brighton", "city", "Brighton", "CO"),
        (r"big sky", "Town of Big Sky", "city", "Big Sky", "MT"),
        (r"camden loop|camden", "City of Camden", "city", "Camden", "NJ"),
        (r"centro move|centro", "Centro", "transit_agency", "Syracuse", "NY"),
        (r"cherriots|salem.*or", "Cherriots", "transit_agency", "Salem", "OR"),
        (r"citilink|fort wayne", "Citilink", "transit_agency", "Fort Wayne", "IN"),
        (r"cota plus|cota", "Central Ohio Transit Authority", "transit_agency", "Columbus", "OH"),
        (r"cata rydz|lansing", "Capital Area Transportation Authority", "transit_agency", "Lansing", "MI"),
        (r"catago|state college", "Centre County Transportation Authority", "transit_agency", "State College", "PA"),
        (r"cecil transit|cecil county", "Cecil County", "county", "Cecil County", "MD"),
        (r"cobblinc|cobb county", "Cobb County", "county", "Cobb County", "GA"),
        (r"connect transit|bloomington|normal", "Connect Transit", "transit_agency", "Bloomington", "IL"),
        (r"connect torrance|torrance", "Torrance Transit", "transit_agency", "Torrance", "CA"),
        (r"dart on demand|des moines", "Des Moines Area Regional Transit", "transit_agency", "Des Moines", "IA"),
        (r"dcta|denton", "Denton County Transportation Authority", "transit_agency", "Denton", "TX"),
        (r"delaware county transit|delaware", "Delaware County Transit", "transit_agency", "Delaware", "DE"),
        (r"denver connector", "City and County of Denver", "city", "Denver", "CO"),
        (r"durango|durangogo", "City of Durango", "city", "Durango", "CO"),
        (r"brunswick breeze", "City of Brunswick", "city", "Brunswick", "NC"),
        (r"addison orbit", "City of Addison", "city", "Addison", "TX"),
        (r"grtc", "Greater Richmond Transit Company", "transit_agency", "Richmond", "VA"),
        (r"flexride|theride|ann arbor", "Ann Arbor Area Transportation Authority", "transit_agency", "Ann Arbor", "MI"),
        (r"flexride milwaukee", "Milwaukee Transit System", "transit_agency", "Milwaukee", "WI"),
        (r"go west covina", "City of West Covina", "city", "West Covina", "CA"),
        (r"go2|muskegon|mats", "Muskegon Area Transit System", "transit_agency", "Muskegon", "MI"),
        (r"gogastonia|gastonia", "City of Gastonia", "city", "Gastonia", "NC"),
        (r"gomarti|marti", "Marti Regional Transit", "transit_agency", "", ""),
        (r"gltc flex|greenville", "Greenville Transit", "transit_agency", "Greenville", "SC"),
        (r"luzerne|lcta", "Luzerne County Transportation Authority", "transit_agency", "Wilkes-Barre", "PA"),
        (r"okaloosa.*transit", "Okaloosa County Transit", "transit_agency", "Okaloosa County", "FL"),
        (r"palm tran|west palm beach|glades", "Palm Beach County Transit", "transit_agency", "West Palm Beach", "FL"),
        (r"palo alto", "City of Palo Alto", "city", "Palo Alto", "CA"),
        (r"passaic county", "Passaic County", "county", "Passaic County", "NJ"),
        (r"pierce transit", "Pierce Transit", "transit_agency", "Tacoma", "WA"),
        (r"plano rides", "City of Plano", "city", "Plano", "TX"),
        (r"rochester public|rochester", "Rochester Public Transit", "transit_agency", "Rochester", "NY"),
        (r"sacrrt|sac rt", "Sacramento Regional Transit District", "transit_agency", "Sacramento", "CA"),
        (r"salem skipper|salem", "City of Salem", "city", "Salem", "OR"),
        (r"sam transit", "Sam Transit", "transit_agency", "", ""),
        (r"scctd|scrolls", "Santa Clarita County Transit", "transit_agency", "Santa Clarita", "CA"),
    ]

    for pattern, agency_name, atype, c, s in agency_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, country, program_name, "high", notes

    # Try to extract agency name from description if it's mentioned
    if agency_type == "unknown":
        # Look for "Authority", "Transit", "Transportation" patterns
        agency_match = re.search(
            r"(\w+(?:\s+\w+)*?\s+(?:County|Area|Regional)?\s*(?:Transit|Transportation)(?:\s+Authority)?)",
            description,
            re.IGNORECASE
        )
        if agency_match:
            potential_agency = agency_match.group(1).strip()
            # Validate it's a reasonable length
            if 5 < len(potential_agency) < 80:
                agency = potential_agency
                agency_type = "transit_agency"
                confidence = "medium"
                return agency, agency_type, city, state, country, program_name, confidence, notes

    # City extraction from description or name
    if not city and not state:
        # Try common patterns
        city_state_match = re.search(r"(\w+),\s*([A-Z]{2})", name)
        if city_state_match:
            city = city_state_match.group(1)
            state = city_state_match.group(2)

    return agency, agency_type, city, state, country, program_name, confidence, notes

def process_row(row):
    """Process a single CSV row and return output row."""
    track_id = row["trackId"]
    name = row["name"]
    bundle_id = row["bundleId"]
    description = row["description"]

    agency, agency_type, city, state, country, program_name, confidence, notes = extract_agency_info(
        name, bundle_id, description
    )

    # Extract notes about operations
    if not notes and description:
        if "operated by" in description.lower():
            match = re.search(r"operated by ([^.,;]+)", description, re.IGNORECASE)
            if match:
                operator = match.group(1).strip()
                if operator and len(operator) < 100:
                    notes = f"desc: operated by {operator}"
        elif "employed by" in description.lower():
            match = re.search(r"employed by ([^.,;]+)", description, re.IGNORECASE)
            if match:
                notes = f"desc: employed by {match.group(1).strip()}"

    # Determine in_scope
    in_scope = 0
    if country == "US" and agency_type in ["transit_agency", "city", "county", "university", "school_district", "state_dot"]:
        in_scope = 1

    return {
        "trackId": track_id,
        "name": name,
        "agency": agency,
        "agency_type": agency_type,
        "city": city,
        "state": state,
        "country": country,
        "program_name": program_name,
        "in_scope": in_scope,
        "confidence": confidence,
        "notes": notes,
    }

def main():
    input_file = Path("/Users/kwu/Documents/VIA/text/enum/appstore_for_mapping.csv")
    output_file = Path("/Users/kwu/Documents/VIA/text/enum/appstore_targets.csv")

    # Read input
    rows = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Process each row
    output_rows = []
    in_scope_count = 0
    for row in rows:
        output_row = process_row(row)
        output_rows.append(output_row)
        if output_row["in_scope"] == 1:
            in_scope_count += 1

    # Write output
    fieldnames = ["trackId", "name", "agency", "agency_type", "city", "state", "country", "program_name", "in_scope", "confidence", "notes"]
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"rows written: {len(output_rows)}")
    print(f"in_scope: {in_scope_count}")

if __name__ == "__main__":
    main()
