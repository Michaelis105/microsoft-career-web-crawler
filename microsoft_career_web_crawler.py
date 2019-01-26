"""
    Web Crawler intended for Microsoft's Career Page
    Crawls for all software engineer positions that are involved
    with some invitational hiring event
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import json

"""
Experienced Professional = 'professional'
Students and recent graduates = 'university'
"""
#role_type = 'professional'

# Role sought after (e.g. software engineer)
role_name = 'software engineer'

def atoi(s):
    """
        Converts integer jobId as string to integer

        Args:
            s (string): Microsoft jobId
        Returns:
            integer form
    """
    n = 0
    for i in s:
        n = n * 10 + ord(i) - ord("0")
    return n

def getListOfPositions(position_name : str):
    """
        Retrives all Microsoft publicily listed positions with name `position_name`
        by sending POST to Microsoft career endpoint.

        Args:
            position_name (str): Name of the position
            
        Returns:
            List of positions based on position_name and other criteria defined
            in body variables as JSON.

            Note: Actual JSON returned determined by endpoint
    """

    if not position_name:
        print("Please specify a position_name")
        return None

    url = 'https://careers.microsoft.com/widgets'
    
    data = {

        # Edit these fields as you see fit
        "searchType":"professional",
        "keywords": position_name,
        "selected_fields": {
            "country": ["United States"],
            "category": ["Engineering"],
            "employmentType": ["Full-Time"],
            "requisitionRoleType": ["Individual Contributor"]
        },
                           
        # Only change these fields if you know what you are doing
        "lang": "en_us",
        "deviceType": "desktop",
        "country": "us",
        "ddoKey": "refineSearch",
        "sortBy": "Most relevant",
        "subsearch": "",
        "from": 0,
        "jobs": True,
        "counts": True,
        "all_fields": ["country","state","city","category","employmentType","requisitionRoleType","educationLevel"],
        "pageName": "search-results",
        "size": 10000,
        "clearAll": False,
        "jdsource": "facets",
        "isSliderEnable": False,
        "isMostPopular": True,
        "global": True
    }

    data_json = json.dumps(data)
    headers = {'Content-type':'application/json'}
    response = requests.post(url, data=data_json, headers=headers)
    return response.json()


def isMatchingJob(job : dict):
    """
        Determines if Microsoft job matches criteria specified.

        Args:
            job (list): A job
                [0]     = "country"
                [1]     = "subCategory"
                [2]     = "industry"
                [3]     = "title"
                [4]     = "multi_location"
                [5]     = "type"
                [6]     = "orgFunction"
                [7]     = "locale"
                [8]     = "multi_location_array"
                    [N] = "location"
                [9]     = "jobSeqNo"
                [10]    = "postedDate"
                [11]    = "searchresults_display"
                [12]    = "descriptionTeaser"
                [13]    = "dateCreated"
                [14]    = "state"
                [15]    = "targetLevel"
                [16]    = "jd_display"
                [17]    = "reqId"
                [18]    = "badge"
                [19]    = "jobId"
                [20]    = "isMultiLocation"
                [21]    = "jobVisibility"
                    [N] = "external"
                [22]    = "mostpopular"
                [21]    = "location"
                [22]    = "category"
                [23]    = "locationLatlong"
        Returns true if matches some criteria, false otherwise
    """

    '''
        Custom criteria
            - Do not match a senior or specialized titular roles
            - Consider only SDE I-II levels (59-62)
    '''    
    try:
        titleSplit = job["title"].split()
        for title in titleSplit:
            if (title in ("Principal", "Manager", "Senior", "Sr.", "Architect",
                        "DevOps", "Design", "Security", "Service",
                        "Scientist", "SW", "HW", "Hardware", "SRE", "Lead",
                        "Site", "Reliability", "Test", "Cloud", "DCS",
                        "SW/FW", "Mobile", "Network", "Data", "International",
                        "Quantum", "Machine", "UI", "Firmware")):
                return False

        targetLevel = atoi(job["targetLevel"])
        return not (targetLevel < 59 or targetLevel > 62)
    except KeyError as ke:
        print("Error processing job with title: " + job["title"])
        return False
    

jobs_json = getListOfPositions(role_name)

if not jobs_json:
    print('Error loading JSON response from endpoint')
    exit()

unique_titles_temp = set()
matching_job_ids = []
jobs = jobs_json["refineSearch"]["data"]["jobs"]
for job in jobs:
    if isMatchingJob(job):
        matching_job_ids.append(job["jobId"])
        unique_titles_temp.add(job["title"])
        

job_specific_url_root = "https://careers.microsoft.com/us/en/job/"
for job_id in matching_job_ids:
    job_specific_url = job_specific_url_root + job_id
    job_page = urlopen(job_specific_url)
    soup = BeautifulSoup(job_page, 'html.parser')
    print(soup.prettify())
    #print(soup.find('strong'))
    #TODO: Parse for invitation day text

print("List of matched jobs")
print("==========================")
for title in unique_titles_temp:
    print(title)
    
