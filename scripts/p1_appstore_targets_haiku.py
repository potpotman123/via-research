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
        (r"dubai", "Road and Transport Authority", "transit_agency", "Dubai", "", "United Arab Emirates"),
        (r"abu dhabi", "", "private", "", "", "United Arab Emirates"),
        (r"ajman", "", "private", "", "", "United Arab Emirates"),
        (r"bc transit", "BC Transit", "transit_agency", "", "BC", "Canada"),
        (r"boka resa|sl ", "SL", "transit_agency", "Stockholm", "", "Sweden"),
        (r"clicbus|atac", "ATAC", "transit_agency", "Rome", "", "Italy"),
        (r"electromin", "", "private", "", "", "Saudi Arabia"),
        (r"busplus", "", "private", "", "", "France"),
        (r"connect2.*north lincs", "", "private", "", "", "United Kingdom"),
        (r"easy tad|tad", "", "private", "", "", "France"),
        (r"frgflex|freyung", "", "private", "", "", "Germany"),
        (r"quibus|veneto", "", "private", "", "", "Italy"),
        (r"my bus|alte marche|fano|pesaro", "", "private", "", "", "Italy"),
        (r"go! on demand.*sagrado|turriaco", "", "private", "", "", "Italy"),
        (r"my turn rides|dubai", "", "private", "", "", "United Arab Emirates"),
        (r"hellobusbus|tremosine|limone", "", "private", "", "", "Italy"),
        (r"ruse moonset", "", "private", "", "", ""),
        (r"rvm rides", "", "private", "", "", ""),
    ]

    for pattern, agency_name, atype, c, s, ctry in intl_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, ctry, program_name, "high", notes

    # === VIA'S OWN SERVICES ===

    via_own_patterns = [
        r"^via driver$",
        r"^downtowner$",
        r"^field trips",
        r"^shuttle - powered by via$",
        r"^shuttle$",
    ]

    for pattern in via_own_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return "", "via_own", "", "", "", program_name, "high", notes

    # === US SERVICES ===

    country = "US"

    # University services
    university_patterns = [
        (r"marquette", "Marquette University", "university", "Milwaukee", "WI"),
        (r"columbia university|columbia transportation", "Columbia University", "university", "New York", "NY"),
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
        (r"oklahoma.*norman|ou saferide", "University of Oklahoma", "university", "Norman", "OK"),
    ]

    for pattern, agency_name, atype, c, s in university_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, country, program_name, "high", notes

    # Transit agencies and cities - comprehensive list
    agency_patterns = [
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
        (r"flexride milwaukee|milwaukee", "Milwaukee Transit System", "transit_agency", "Milwaukee", "WI"),
        (r"go west covina", "City of West Covina", "city", "West Covina", "CA"),
        (r"go2|muskegon|mats", "Muskegon Area Transit System", "transit_agency", "Muskegon", "MI"),
        (r"gogastonia|gastonia", "City of Gastonia", "city", "Gastonia", "NC"),
        (r"glendale onboard|city of glendale", "City of Glendale", "city", "Glendale", "AZ"),
        (r"gltc flex|greenville.*transit", "Greenville Transit", "transit_agency", "Greenville", "SC"),
        (r"henry connect|henry county", "Henry County", "county", "McDonough", "GA"),
        (r"hoco rapidride|howard county", "Howard County", "county", "Ellicott City", "MD"),
        (r"luzerne|lcta", "Luzerne County Transportation Authority", "transit_agency", "Wilkes-Barre", "PA"),
        (r"middlesex county ride", "Middlesex County", "county", "Middlesex County", "NJ"),
        (r"morrisville smart shuttle", "Town of Morrisville", "city", "Morrisville", "VT"),
        (r"mta smartmove|genesee county", "Genesee County", "county", "Genesee County", "MI"),
        (r"okaloosa.*transit", "Okaloosa County Transit", "transit_agency", "Okaloosa County", "FL"),
        (r"palm tran|west palm beach|glades", "Palm Beach County Transit", "transit_agency", "West Palm Beach", "FL"),
        (r"palo alto", "City of Palo Alto", "city", "Palo Alto", "CA"),
        (r"passaic county", "Passaic County", "county", "Passaic County", "NJ"),
        (r"pierce transit", "Pierce Transit", "transit_agency", "Tacoma", "WA"),
        (r"plano rides", "City of Plano", "city", "Plano", "TX"),
        (r"rochester public|rochester", "Rochester Public Transit", "transit_agency", "Rochester", "NY"),
        (r"sacrt|sac rt", "Sacramento Regional Transit District", "transit_agency", "Sacramento", "CA"),
        (r"salem skipper|salem", "City of Salem", "city", "Salem", "OR"),
        (r"sam transit", "Sam Transit", "transit_agency", "", ""),
        (r"scctd|scrolls", "Santa Clarita County Transit", "transit_agency", "Santa Clarita", "CA"),
        (r"ride the line|missoula", "Mountain Line MTD", "transit_agency", "Missoula", "MT"),
        (r"ride wilson|wilson", "Town of Wilson", "city", "Wilson", "NC"),
        (r"shift on demand|philadelphia", "City of Philadelphia", "city", "Philadelphia", "PA"),
        (r"shuttle connection", "Shuttle Connection", "transit_agency", "", ""),
        (r"sunnyvale beam|sunnyvale", "City of Sunnyvale", "city", "Sunnyvale", "CA"),
        (r"sunride|sunline", "SunLine Transit Agency", "transit_agency", "Palm Springs", "CA"),
        (r"sypn ondemand|york.*penn", "Southern York Public Network", "transit_agency", "York", "PA"),
        (r"tarta flex|toledo", "Toledo Area Regional Transit Authority", "transit_agency", "Toledo", "OH"),
        (r"terp ride|maryland", "University of Maryland", "university", "College Park", "MD"),
        (r"trinity metro", "Trinity Metro", "transit_agency", "Fort Worth", "TX"),
        (r"uta mav mover|uta on demand|uta.*arlington", "University of Texas at Arlington", "university", "Arlington", "TX"),
        (r"uw.*madison.*accessible|wisconsin.*madison", "University of Wisconsin-Madison", "university", "Madison", "WI"),
        (r"valdosta", "City of Valdosta", "city", "Valdosta", "GA"),
        (r"via grand prairie", "City of Grand Prairie", "city", "Grand Prairie", "TX"),
        (r"via jersey city", "City of Jersey City", "city", "Jersey City", "NJ"),
        (r"via metro stl|via.*st louis", "City of St. Louis", "city", "St. Louis", "MO"),
        (r"via newark|newark.*new jersey", "City of Newark", "city", "Newark", "NJ"),
        (r"via nhv|new haven", "City of New Haven", "city", "New Haven", "CT"),
        (r"via san diego", "City of San Diego", "city", "San Diego", "CA"),
        (r"via west sac|west sacramento", "City of West Sacramento", "city", "West Sacramento", "CA"),
        (r"visalia connect", "City of Visalia", "city", "Visalia", "CA"),
        (r"wrta|worcester", "Worcester Regional Transit Authority", "transit_agency", "Worcester", "MA"),
        (r"gbm transit|green bay", "Green Bay Metro", "transit_agency", "Green Bay", "WI"),
        (r"gift on-demand|idaho falls", "City of Idaho Falls", "city", "Idaho Falls", "ID"),
        (r"gomarti|northern minnesota|minn", "Marti Regional Transit", "transit_agency", "", "MN"),
        (r"howl-a-ride|stony brook", "Stony Brook University", "university", "Stony Brook", "NY"),
        (r"key west rides", "City of Key West", "city", "Key West", "FL"),
        (r"lanow|los angeles|la metro", "Los Angeles County Metropolitan Transportation Authority", "transit_agency", "Los Angeles", "CA"),
        (r"lynx by cats|baker.*louisiana", "Catahoula Transit System", "transit_agency", "Baker", "LA"),
        (r"max on-demand|jefferson county.*missouri", "City of Kansas City", "city", "Kansas City", "MO"),
        (r"met go", "Monmouth County", "county", "Monmouth County", "NJ"),
        (r"metroconnect.*miami|miami-dade", "Miami-Dade County", "county", "Miami", "FL"),
        (r"metro link.*kalamazoo", "Kalamazoo Public Transit", "transit_agency", "Kalamazoo", "MI"),
        (r"micro flex.*omaha", "Omaha", "city", "Omaha", "NE"),
        (r"microlink", "MicroLink", "transit_agency", "", ""),
        (r"mobilid", "MobiliD", "private", "", ""),
        (r"rc link", "RC Link", "transit_agency", "", ""),
        (r"ready.*mataplus|mata", "Madisonville Transit Authority", "transit_agency", "Madisonville", "LA"),
        (r"rekab solutions", "Rekab Solutions", "private", "", ""),
        (r"richmond moves", "GRTC", "transit_agency", "Richmond", "VA"),
        (r"ride jaunt", "Ride Jaunt", "private", "", ""),
        (r"ride longmont", "City of Longmont", "city", "Longmont", "CO"),
        (r"ride on flex", "Montgomery County", "county", "Montgomery County", "MD"),
        (r"ride rf", "Ride RF", "transit_agency", "", ""),
        (r"mets micro", "Metropolitan Transportation Commission", "transit_agency", "", ""),
        (r"may mobility", "May Mobility", "private", "", ""),
        (r"lhc direct", "Lawrence-Harvard Consultants", "private", "", ""),
        (r"nyc school bus", "New York City Department of Education", "city", "New York", "NY"),
        (r"rts on demand|rochestert", "Rochester Regional Transit", "transit_agency", "Rochester", "NY"),
        (r"start on-demand|jackson.*mississippi", "City of Jackson", "city", "Jackson", "MS"),
        (r"stevens shuttle|hoboken", "Stevens Institute of Technology", "university", "Hoboken", "NJ"),
        (r"the buc|buckhead", "City of Buckhead", "city", "Buckhead", "GA"),
        (r"wego.*powered by via", "City of Nashville", "city", "Nashville", "TN"),
        (r"groove.*memphis", "City of Memphis", "city", "Memphis", "TN"),
        (r"mountain climber|kalispell|whitefish", "Mountain Climber", "transit_agency", "Kalispell", "MT"),
        (r"slidr rides", "Slidr Rides", "private", "", ""),
        (r"via2g", "", "via_own", "", ""),
        (r"wexexpress|wexford", "Wexford County", "county", "Wexford County", "MI"),
        (r"wheels2u|norwalk|westport", "City of Norwalk", "city", "Norwalk", "CT"),
        (r"winready|winchester", "City of Winchester", "city", "Winchester", "VA"),
        (r"yav connect|prescott valley", "Town of Prescott Valley", "city", "Prescott Valley", "AZ"),
        (r"zip shuttle|snohomish", "Snohomish County", "county", "Snohomish County", "WA"),
        (r"metro connect|rock region", "Rock Region METRO", "transit_agency", "St. Louis", "MO"),
        (r"tyler transit", "City of Tyler", "city", "Tyler", "TX"),
    ]

    for pattern, agency_name, atype, c, s in agency_patterns:
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, desc_lower):
            return agency_name, atype, c, s, country, program_name, "high", notes

    # Generic extraction from description
    if agency_type == "unknown":
        # Look for City/County patterns
        city_match = re.search(r"(?:City|Town) of (\w+)", description)
        if city_match:
            agency = f"City of {city_match.group(1)}"
            agency_type = "city"
            confidence = "medium"
            return agency, agency_type, city_match.group(1), state, country, program_name, confidence, notes

        county_match = re.search(r"(\w+(?:\s+\w+)*?)\s+County", description)
        if county_match:
            agency = f"{county_match.group(1)} County"
            agency_type = "county"
            city = county_match.group(1)
            confidence = "medium"
            return agency, agency_type, city, state, country, program_name, confidence, notes

        # Look for transit authority patterns
        transit_match = re.search(
            r"(\w+(?:\s+\w+)*?)\s+(?:Transit|Transportation)(?:\s+Authority)?",
            description,
            re.IGNORECASE
        )
        if transit_match:
            potential_agency = transit_match.group(1).strip()
            if 5 < len(potential_agency) < 80:
                agency = potential_agency
                agency_type = "transit_agency"
                confidence = "medium"
                return agency, agency_type, city, state, country, program_name, confidence, notes

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
