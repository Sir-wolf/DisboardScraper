# import module
import sys
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup
from schema import Schema, Or, And, Use
from tqdm import tqdm

import optparse

# esthetic function
class color:
    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    LOGGING = '\33[34m'

def clearScr():
    os.system('clear')

# argument function
def get_arguments():
    parser = optparse.OptionParser()


    parser.add_option("-t", "--tag", dest="tag", help="This is the tag you want to analyze for servers.(str)")
    parser.add_option("-p", "--pages", dest="pages", help="This configures how many pages for a tag you want to scrape.(int)")
    
    parser.add_option("-o", "--top_positional_tags", dest="top_positional_tags", help="This displays the most popular tags for each tag's position. (True, False)")
    
    parser.add_option("-l", "--tpt_limit", dest="tpt_limit", help="This displays the most popular tags for each tag's position. (int)")
    parser.add_option("-c", "--csv", dest="csv", help="When enabled will output all scraped data into a CSV file. This should make further analysis easier. (True, False)")
    parser.add_option("-d", "--debug", dest="debug", help="While set to true the script will display more output onto the console for debugging purposes. This will also disable the progress bar. (True, False)")

    (options, arguments) = parser.parse_args()
    if not options.tag:
        parser.error(color.NOTICE + "[-] Please specify the information, use --help for more info" + color.END)
    return options

options = get_arguments()

logo = color.HEADER + '''
____  _     _                         _ ____                                 
|  _ \(_)___| |__   ___   __ _ _ __ __| / ___|  ___ _ __ __ _ _ __   ___ _ __ 
| | | | / __| '_ \ / _ \ / _` | '__/ _` \___ \ / __| '__/ _` | '_ \ / _ \ '__|
| |_| | \__ \ |_) | (_) | (_| | | | (_| |___) | (__| | | (_| | |_) |  __/ |   
|____/|_|___/_.__/ \___/ \__,_|_|  \__,_|____/ \___|_|  \__,_| .__/ \___|_|   
                                                            |_|   
                                                            
    ''' + color.END

print (logo + color.RED + '''
    }--------------{+} Coded By Sirwolf {+}--------------{
    }--------{+}    GitHub.com/Sir-wolf :)    {+}--------{
    ''' + color.END)



# Configurations
tag = str(options.tag)
pages = int(options.pages)

if options.top_positional_tags == "t" :
    top_positional_tags = True
else: 
    top_positional_tags = False

tpt_limit = int(options.tpt_limit)

if options.csv == "t" :
    csv = True
else: 
    csv = False

if options.debug == "t" :
    debug = True
else: 
    debug = False


# Constants
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Variables
servers = []

# Progress Bar
print(f"Fetching {pages} Pages: \n")
if not debug:
    bar = tqdm(total=pages)

# Iterate over each page for a tag
for page in range(1, pages + 1):
    url = f"https://disboard.org/servers/tag/{tag}/{page}?sort=-member_count"
    request = Request(url, headers=HEADERS)
    resource = urlopen(request)
    content = resource.read().decode(resource.headers.get_content_charset())
    soup = BeautifulSoup(content, 'html.parser')

    # Iterate over each server
    for server_info in soup.find_all(class_='server-info'):
        server_name = server_info.find(class_="server-name")
        server_name_link = server_name.find('a')
        server_online = server_info.find(class_="server-online")

        parent = server_info.parent.parent
        tags = []
        for tag_ in parent.find_all(class_="tag"):
            tag_name = tag_.find(class_="name")
            tags.append(tag_name.contents[0].strip())

        # Check servers without online counts
        if hasattr(server_online, 'contents'):
            members_online_count = server_online.contents[0].strip()
        else:
            members_online_count = "N/A"

        # Create a server
        server = [
            server_name_link.contents[0].strip(),
            members_online_count
        ]
        server.extend(tags)

        if debug:
            print(f"Server: {server}")

        # Add each server found
        servers.append(server)

    # Increment Progress
    if not debug:
        bar.update(1)

df = pd.DataFrame(
    servers,
    columns=[
        'Server Name',
        'Members Online',
        'Tag 1',
        'Tag 2',
        'Tag 3',
        'Tag 4',
        'Tag 5'
    ]
)

# Close Progress Bar
if not debug:
    bar.close()

if top_positional_tags:
    print("\n== Top Tags by Position ==")
    for i in range(1, 6):
        print(f"Tag {i}: ")
        print(f"{str(df[f'Tag {i}'].value_counts()[:tpt_limit])}\n")

if csv:
    print("Creating output file...")
    df.to_csv(f'{tag}_servers.csv', index=False, encoding='utf-8-sig')
    print(f"Done writing: {tag}_servers.csv")
else:
    print("Exiting without writing file!")
