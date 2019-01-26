"""
    Web Crawler intended for Microsoft's Career Page
    Crawls for all entry-level software engineer positions
    involved with some invitation-only hiring event
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import json
import datetime

def atoi(s : str):
    """
        Converts integer jobId as string to integer

        Args:
            s (string): Microsoft jobId
            
        Returns:
            integer form
    """
    if not s:
        print("Cannot convert empty string to integer")
    
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

    # Microsoft careers endpoint
    url = 'https://careers.microsoft.com/widgets'

    # Specific JSON data is expected by endpoint
    data = {

        # Edit these fields as you see fit.
        # They must conform to existing data fields found on career page
        "searchType":"professional", #professional or university
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
        "from": 0, # Return the first `from` to `size` results.
                   # Change this field iteratively if displaying only smaller portions of `size` results
        "jobs": True,
        "counts": True,
        "all_fields": ["country","state","city","category","employmentType","requisitionRoleType","educationLevel"],
        "pageName": "search-results",
        "size": 10000, # Use small numbers when testing - don't be a jerk to Microsoft.
                       # Preferred max is 10000.
                       # Note: This returns first `size` results that Microsoft returns
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
            job (list): A job in JSON returned by Microsoft career endpoint
                
        Returns:
            - true if matches some criteria
            - false otherwise
    """

    '''
        Custom criteria
            - Do not match senior or similar, specialized titular roles
            - Consider only SDE I-II levels (59-62) (this is hidden to user)
    '''    
    try:
        titleSplit = job["title"].split()
        for title in titleSplit:
            if (title in ("Principal", "Manager", "Senior", "Sr.", "Architect",
                        "DevOps", "Design", "Security", "Service",
                        "Scientist", "SW", "HW", "Hardware", "SRE", "Lead",
                        "Site", "Reliability", "Test", "Cloud", "DCS",
                        "SW/FW", "Mobile", "Network", "Data", "International",
                        "Quantum", "Machine", "UI", "UX", "Firmware",
                        "High-Performance", "C++")):
                return False

        targetLevel = atoi(job["targetLevel"])
        return not (targetLevel < 59 or targetLevel > 62)
    except KeyError as ke:
        print("Error processing job with title: " + job["title"])
        return False


def isMatchingJobInterviewDay(job_url : str):
    """
        Determines if job description mentions anything pertaining to
        an invitation-only interview day

        Args:
            job_url (string): URL to specific Microsoft position
        
    """
    if not job_url:
        print("Cannot check empty job_url")
        return False
    
    try:
        job_page = urlopen(job_specific_url)
        soup = BeautifulSoup(job_page, 'html.parser')

        # Microsoft hid job description information in JavaScript.
        # Assuming something has to render it first to display to user.
        # Search entire script value - very inefficient!
        script = soup.find("script", type="text/javascript")        
        return script.text.find("By applying to this position") != -1
        # TODO: Enhance to ignore all past interview days
    except:
        # Frequent 502 errors occur, need some way to retry.
        print("Error processing url: " + job_specific_url)
        
    return False

beginTime = datetime.datetime.now()
print("Starting web crawl:\t" + str(beginTime))

role_name = 'software engineer'
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
    if isMatchingJobInterviewDay(job_specific_url):
        print(job_specific_url)

print("\nList of matched jobs")
print("==========================")
for title in unique_titles_temp:
    print(title)

endTime = datetime.datetime.now()
print("\nEnding web crawl:\t" + str(endTime))
print("\nTime elapsed: \t" + str(endTime - beginTime))
              
