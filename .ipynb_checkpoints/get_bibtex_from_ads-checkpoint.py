import requests
import os
import re
import json
import argparse
from urllib.parse import quote

class ArgumentError(Exception):
    pass


##################################################################################
############################ The main rountine ###################################
##################################################################################

def get_bibtex_from_ads(bibstem, volume, page, verbose=False):

    ###### initialization
    url_to_get_access_token = "https://ui.adsabs.harvard.edu/v1/accounts/bootstrap"
    url_to_get_bibcode = f"https://ui.adsabs.harvard.edu/v1/search/query?__clearBigQuery=true&fl=identifier%2C%5Bcitations%5D%2Cabstract%2Cauthor%2Cbook_author%2Corcid_pub%2Corcid_user%2Corcid_other%2Cbibcode%2Ccitation_count%2Ccomment%2Cdoi%2Cid%2Ckeyword%2Cpage%2Cproperty%2Cpub%2Cpub_raw%2Cpubdate%2Cpubnote%2Cread_count%2Ctitle%2Cvolume%2Clinks_data%2Cesources%2Cdata%2Ccitation_count_norm%2Cemail%2Cdoctype&q=bibstem%3A{bibstem}%20volume%3A{volume}%20page%3A{page}&rows=25&sort=date%20desc%2C%20bibcode%20des"
    url_to_get_bibtex = "https://ui.adsabs.harvard.edu/v1/export/bibtex"

    headers = {
        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
    }

    ###### get the access token ######
    session = requests.Session()
    access_token = session.get(url_to_get_access_token, headers=headers)
    if access_token.status_code == 200:
        r_json = access_token.json()
        authorization = f"Bearer:{r_json['access_token']}"
        if verbose:
            print("Successfully get the access token ...")
    else:
        print(f"Failed to get the access token, status_code = {access_token.statsu_code}")

    ###### update the headers by adding Authorization ######
    headers['Authorization'] = authorization

    ###### get the bibcode ######
    get_bibcode = session.get(url_to_get_bibcode, headers=headers)
    if get_bibcode.status_code == 200:
        bib_json = get_bibcode.json()
        bibcode = bib_json['response']['docs'][0]['bibcode']
        if verbose:
            print("Successfully get the bibcode ...")
    else:
        print(f"Failed to get the bibcode, status_code = {get_bibcode.status_code}")

    ###### data for post ######
    data = {
        "authorcutoff": [200],
        "bibcode": [bibcode],
        "journalformat": [1],
        "maxauthor": [0],
        "sort": ["date desc, bibcode desc"]
    }

    ###### post request to get the bibtex ######
    citetext = session.post(url_to_get_bibtex, headers=headers, json=data)
    if citetext.status_code == 200:
        pattern = r'@[A-Z]+{.+\\n}\\n\\n'
        export = re.search(pattern, citetext.text)
        bibtex = export.group()
        # remove some escape character
        bibtex = bibtex.replace("\\n", "\n")
        bibtex = bibtex.replace('\\"', '"')
        bibtex = bibtex.replace('\\\\"', '\\')
        if verbose:
            print("Successfully get the bibtex ...\n\n")
        print("")
        print(bibtex)
    else:
        print(f"Failed to get the bibcode, status_code = {citetext.status_code}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A python script to get the bibtex of a paper from ADS')
    parser.add_argument('--bibstem', type=str, help='The bibstem of the paper')
    parser.add_argument('--volume', type=int, help='The volume of the paper')
    parser.add_argument('--page', type=str, help='The page of the paper')
    parser.add_argument('--verbose', type=str, help='Whether to print logs')
    
    args = parser.parse_args()
    
    # Deal with some special characters like &
    # They need to be converted to url encoding to correctly get the bibcode
    bibstem_url = quote(args.bibstem)
    
    if (args.bibstem==None) or (args.volume==None) or (args.page==None):
        raise ArgumentError("Arguments not complete! Please provide bibstem, volume, and page")
    elif args.verbose:
        get_bibtex_from_ads(bibstem_url, args.volume, args.page, args.verbose)
    else:
        get_bibtex_from_ads(bibstem_url, args.volume, args.page)



