#https://linkedin-api.readthedocs.io/en/latest/api.html
#https://github.com/tomquirk/linkedin-api

import pandas as pd #Pandas DataFrame
import re #RegexLibrary
import importlib
from datetime import datetime #Convert UTCtimeStap - humanTime
from linkedin_api import Linkedin #API LI
import sys
import tkinter as tk
from tkinter import filedialog

writeFolder = 'D:\Python Scripts\Resources'
linkedInUser = 'test.script.2023@gmail.com'
linkedInPass = '$TestPass2023'
# sys.path.append('/Users/karlaprado/Documents/Learning/Data Science Python/modules') 
sys.path.append('D:\Python Scripts')
import linked_in_api as lip
importlib.reload(lip)

#https://www.linkedin.com/search/results/all/?keywords=Cloud%20outcomes%20Accenture&origin=GLOBAL_SEARCH_HEADER&sid=%3A.P
#keywords = [] #Keywords to filer, leave empty if you dont need filtering
#lip.CreateCSVProfilePosts("jimmy-etheredge", [])
#lip.CreateCSVCompanyPosts("deloitte", ['generative AI', 'chatGPT', 'GPT', 'open AI', 'large language models', 'openAI', 'GPT3','open artificial intelligence'])
#lip.CreateCSVProfilePosts("jimmy-etheredge", [])[ "tech trends 2023", "innovation", "artificial intelligence", "sustainable ai", "internet of things", "iot", "virtual reality", "cybersecurity", "digital transformation", "blockchain", "machine learning", "data analytics", "automation", "augmented reality", "ar", "edge computing", "metaverse", "nfts", "cloud computing", "quantum computing", "robotics", "5g", "5g networks", "health tech", "techtrends2023", "#ai" ,"artificialintelligence", "sustainableai", "internetofthings","virtualreality", "digitaltransformation", "blockchain", "machinelearning", "dataanalytics", "augmentedreality", "edgecomputing", "cloudcomputing", "quantumcomputing", "5gnetworks", "healthtech"]
#lip.SearchLinkedInPosts("Cloud outcomes Accenture", []) 

def StartProgram():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)

    
    print("""
    1. Profile
    2. Company
    3. Exit/Quit
    """)
    ans = input("What would you like to do? ")
    if ans == "1":
        print("\n Working on the Profile...")
        profile = input("What is the Profile LinkedIn name, eg. jimmy-etheredge? ")
        postNumber = int(input("Number of posts to get, eg. 10? "))
        CreateCSVProfilePosts(profile, [], postNumber)
        print("\n Profile completed")
        ans = True
    elif ans == "2":
        print("\n Working on the Company...")
        profile = input("What is the Company LinkedIn name, eg. deloitte? ")
        CreateCSVCompanyPosts(profile,  [])
        print("\n Company completed")
        print("\n Goodbye") 
        ans = False
    elif ans == "3":
        print("\n Goodbye")
        ans = False
    else:
        print("\n Not Valid Choice Try again")

# Get posts of a personal progile, able to filter them *******************************************************************************************************************************************

def CreateCSVProfilePosts(profileName, keywords, postNumber):
    api = Linkedin(linkedInUser, linkedInPass) #Login
    posts = api.get_profile_posts(profileName, post_count=postNumber)

    columns = ['DateTime', 'PostURL', 'PostCopy', 'Likes', 'Comments']
    df = pd.DataFrame(columns)
    finalList = []
    index = 0
    for x in posts:
        # print(x['updateMetadata']['updateActions']['actions'])
        actions = x['updateMetadata']['updateActions']['actions']
        url = ''
        for action in actions:
            if action['actionType'] == 'SHARE_VIA':
                url = action['url']
                break
        text = ""
        if 'commentary' in x:
            text = x['commentary']['text']['text']
        likes = x['socialDetail']['totalSocialActivityCounts']['numLikes']
        comments = x['socialDetail']['totalSocialActivityCounts']['numComments']
        dateTimePost = GetLinkedInDate(url)
        finalList.append({'DateTime': dateTimePost, 'PostURL' : url, 'PostCopy': text, 'Likes' : likes, 'Comments' : comments})
        index = index + 1
    
    df = pd.DataFrame.from_records(finalList)
    df = FilterByKeywords(keywords, df, "text")

    #df.to_csv('/Users/karlaprado/bin/LinkedIn' + profileName + 'Posts.csv', index=False, encoding='utf-8-sig')
    print("\n Please select folder to save the results.")
    writeFolder = filedialog.askdirectory(title='Select Folder to save the results')
    df.to_csv(writeFolder + '\CompanyLinkedIn_' + profileName + 'Posts.csv', index=False, encoding='utf-8-sig')


# Get posts of a company, able to filter them *******************************************************************************************************************************************

def CreateCSVCompanyPosts(companyName, keywords):
    api = Linkedin(linkedInUser, linkedInPass) #Login
    posts = api.get_company_updates(companyName)
    
    columns = ['DateTime', 'PostURL', 'PostCopy', 'Likes', 'Comments']
    df = pd.DataFrame(columns)
    finalList = []
    index = 0
    for x in posts:
        permaLink = x['permalink']
        url = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['updateMetadata']['updateActions']['actions'][1]['url']
        text = ""
        if 'commentary' in x['value']['com.linkedin.voyager.feed.render.UpdateV2']:
            text = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['commentary']['text']['text']
        likes = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['socialDetail']['totalSocialActivityCounts']['numLikes']
        comments = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['socialDetail']['totalSocialActivityCounts']['numComments']
        dateTimePost = GetLinkedInDate(permaLink)
        finalList.append({'DateTime': dateTimePost, 'PostURL' : url, 'PostCopy': text, 'Likes' : likes, 'Comments' : comments})
        index = index + 1
    
    df = pd.DataFrame.from_records(finalList)
    df = FilterByKeywords(keywords, df, "text")
    
    #df.to_csv('/Users/karlaprado/bin/LinkedIn' + companyName + 'Posts.csv', index=False, encoding='utf-8-sig')
    print("\n Please select folder to save the results.")
    writeFolder = filedialog.askdirectory(title='Select Folder to save the results')
    df.to_csv(writeFolder + '\CompanyLinkedIn_' + companyName + '_Activity.csv', index=False, encoding='utf-8-sig')

# Get posts of a company, able to filter them *******************************************************************************************************************************************

def SearchLinkedInPosts(searchText, keywords):
    api = Linkedin(linkedInUser, linkedInPass) #Login
    posts = api.search({ "keywords": searchText, "origin": "GLOBAL_SEARCH_HEADER" } , limit = 1000)
    return posts
    
    columns = ['datetime', 'permalink', 'url', 'text', 'likes', 'comments']
    df = pd.DataFrame(columns)
    finalList = []
    index = 0
    for x in posts:
        permaLink = x['permalink']
        url = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['updateMetadata']['updateActions']['actions'][1]['url']
        text = ""
        if 'commentary' in x['value']['com.linkedin.voyager.feed.render.UpdateV2']:
            text = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['commentary']['text']['text']
        likes = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['socialDetail']['totalSocialActivityCounts']['numLikes']
        comments = x['value']['com.linkedin.voyager.feed.render.UpdateV2']['socialDetail']['totalSocialActivityCounts']['numComments']
        dateTimePost = GetLinkedInDate(permaLink)
        finalList.append({'datetime': dateTimePost, 'permalink': permaLink, 'url' : url, 'text': text, 'likes' : likes, 'comments' : comments})
        index = index + 1
    
    df = pd.DataFrame.from_records(finalList)
    df = FilterByKeywords(keywords, df, "text")
    
    #df.to_csv('/Users/karlaprado/bin/LinkedIn' + companyName + 'Posts.csv', index=False, encoding='utf-8-sig')
    df.to_csv(writeFolder + '\SearchLinkedIn_' + searchText + '_Activity.csv', index=False, encoding='utf-8-sig')

# Get LinkedIn date *******************************************************************************************************************************************

def GetLinkedInDate(linkedInLink) :
    dateTimePost = datetime.fromordinal(730920).strftime('%Y-%m-%d %H:%M:%S')
    regexResult = re.search("([0-9]{19})", linkedInLink)
    if regexResult:
        postId = int(regexResult.group())
        asBinary = "{0:b}".format(postId)
        first41Chars = asBinary[0:41]
        timestamp = int(first41Chars, 2)
        pythonTimestamp = timestamp / 1000.0
        dateTimePost = datetime.utcfromtimestamp(pythonTimestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    return dateTimePost

# Filter by keywords or text *******************************************************************************************************************************************
def FilterByKeywords(keywordList, dataFrame, columnToFilter) :
    if (len(keywordList) > 0) :
        searchPattern = '|'.join(keywordList)
        #
        filter = dataFrame[columnToFilter].str.contains(searchPattern, flags=re.IGNORECASE, regex=True)
        dataFrame = dataFrame[filter]
    
    return dataFrame


lip.StartProgram()
#keywordTest = ['generative AI', 'chatGPT', 'GPT', 'open AI', 'large language models', 'openAI', 'GPT3','open artificial intelligence']
#searchPattern = '|'.join(keywordTest)
#print(searchPattern)