"""
VirusTotal API Integration
Author: Phantom0004 (Daryl Gatt)

Description:
This module integrates with VirusTotal's API to analyze files and URLs, retrieving 
threat intelligence such as file hashes, URL reputations, crowdsourced YARA rules, 
and threat classifications. It complements existing malware detection frameworks 
by providing detailed insights into malicious attributes and behaviors.

Features:
- Analyze files and URLs for malicious indicators.
- Retrieve crowdsourced intelligence, including YARA rules and threat mappings.
- Classify threats using popular labels and categories.
- Parse and display detailed analysis results.

Usage:
- Use this module to interact with VirusTotal's API for threat analysis.
- Retrieve and display insights to enhance malware detection workflows.
"""

try:
    import vt
    import requests
    from termcolor import colored
except ModuleNotFoundError:
    exit(f"'virus_total.py' Library Error -> Please install all requirements via the 'requirements.txt' file with PIP")

from urllib.parse import urlparse, quote
import hashlib 
import json
import os

class VirusTotalAPI:
    def __init__ (self, choice="1", data="placeholder", API_KEY="", client_obj=""):
        self.API_KEY = API_KEY
        self.data = data
        self.choice = choice
        self.client_obj = client_obj
    
    # Verify and Connect to API Endpoint 
    def connect_to_endpoint(self):
        try:
            conn_object, status = vt.Client(self.API_KEY), "success"
            print(colored("✔ Connected to VirusTotal API Successfully \n", "green", attrs=["bold"]))
            return conn_object, status
        
        # VT library Related Exceptions
        except vt.error.APIError as vt_error:
            print(colored("✘ API Error: Updating vt-py library to try fix issue ...", "yellow", attrs=["bold"]))
            os.system("pip install --upgrade vt-py") # Can fix common VT library issues
            try:
                conn_object = vt.Client(self.API_KEY)
                print(colored("✔ Fix Completed - API Connected Successfully \n", "green", attrs=["bold"]))
                return conn_object, "success"
            except:
                print(colored("✘ Fix Failed - Failed to reconnect to VirusTotal API \n", "red", attrs=["bold"]))
                return vt_error, "api_fail"
        
        # General Exceptions    
        except NameError as err:
            return err, "api_fail"
        except Exception as err:
            return err, "general_fail"
    
    # Craft Dynamic API Request
    def craft_api_request(self):
        choice = self.choice.lower()
        data = self.data
        
        if choice not in ["files", "urls"]:
            return "option_fail"
        
        request_string = ""
        if choice == "files":
            request_string = f"/{choice}/{data}"
        elif choice == "urls":
            request_string = f"/{choice}/{vt.url_id(data)}"
            
        try:
            # Force typecast to ensure it is string
            return str(request_string)
        except:
            return request_string

    # Send Request Using vt Library
    def send_api_request_using_vt(self, api_string):
        client_object = self.client_obj
        
        try:
            output = client_object.get_object(api_string)
            return output, "success"
        except vt.error.APIError as vt_error:
            return vt_error, "api_fail"
        except Exception as err:
            return err, "general_fail"
        finally:
            client_object.close()

    # Parse a wide range of API errors
    @staticmethod
    def parse_API_error(exception_string):
        error_message = str(exception_string)
        
        if "Resource not found" in error_message:
            return "The requested resource (file or URL) was not found in VirusTotal's database."
        elif "Forbidden" in error_message or "403" in error_message:
            return "Access is forbidden. This might be due to an invalid API key or insufficient permissions."
        elif "Quota exceeded" in error_message or "429" in error_message:
            return "API quota exceeded. You have reached the limit of requests allowed by your API key. Please try again later."
        elif "Bad request" in error_message or "400" in error_message:
            return "Bad request. The request was malformed or missing required parameters."
        elif "Unauthorized" in error_message or "401" in error_message:
            return "Unauthorized access. The API key provided is invalid or missing."
        elif "Internal server error" in error_message or "500" in error_message:
            return "Internal server error. There was an issue on VirusTotal's side. Please try again later."
        elif "Service Unavailable" in error_message or "503" in error_message:
            return "Service unavailable. VirusTotal's service is temporarily unavailable. Please try again later."
        elif "NotFoundError" in error_message:
            return "The content you are looking for cannot be found or has not been scanned yet in the VirusTotal database. Please submit a Sample."
        elif "Wrong API key" in error_message:
            return "Incorrect API Key entered. Your API key is unknown to VirusTotal. Please enure you copied the value well, and ensure you did not skip the balance."
        else:
            return f"An unknown error occurred: {error_message}"

    # Identify a rough estimate of the criticality of the file
    @staticmethod
    def score_verdict(score_value):
        if not score_value:
            return None
        
        score_value = float(score_value)
        
        if score_value < -10:
            return colored(f"Bad Scoring (Score: {score_value})", 'red')
        elif -10 <= score_value < 0:
            return colored(f"Possibly Bad Scoring (Score: {score_value})", 'light_red')
        elif 0 <= score_value <= 10:
            return colored(f"Neutral Scoring (Score: {score_value})", 'yellow')
        else:
            return colored(f"Good Scoring (Score: {score_value})", 'green')
    
    # Hash file with any 3 algorithims 
    @staticmethod    
    def hash_file(file_data, hash_algo="sha256"):        
        if not isinstance(file_data, bytes):
            try:
                file_data = file_data.encode()
            except:
                pass

        hash_object = None
        try:
            if hash_algo == "sha256":
                hash_object = hashlib.sha256(file_data)
            elif hash_algo == "md5":
                hash_object = hashlib.md5(file_data)
            elif hash_algo == "sha1":
                hash_object = hashlib.sha1(file_data)
        except:
            return "hashing_error"

        if hash_object is not None:
            try:
                return hash_object.hexdigest()
            except:
                return "hash_digest_error"
        else:
            return "hash_digest_error"

    # Calculate final verdict based on numerical value
    @staticmethod
    def final_verdict(last_analysis_result):
        malicious_count = 0
        
        for _, value in last_analysis_result.items():
            if value.get("category", "") == "malicious":
                malicious_count += 1
        
        if malicious_count < 30:
            print(f"[+] Final Verdict : {colored('Deemed Safe', 'green')} (Marked Malicious by less than 30% of vendors)")
        elif malicious_count in range(30,80):
            print(f"[+] Final Verdict : {colored('Deemed Possibly Malicious', 'yellow')} (Marked Malicious by 30% to 70% of vendors)")
        else:
            print(f"[+] Final Verdict : ({colored('Deemed Likely Malicious', 'red')} (Marked Malicious by over 80% of vendors)")

    # Classify threat based on categories, labels and threat names
    @staticmethod
    def classify_threat(threat_output):
        categories, labels, threat_names = set(), set(), set()

        if not threat_output:
            print("No Threat Intel Found.")
            return
        
        for index , (key, value) in enumerate(threat_output.items()):
            if index >= 5 : break
            if key == "suggested_threat_label":
                labels.add(value)
            elif key == "popular_threat_name" and isinstance(value, list):
                for item in value:
                    threat_names.add(item.get("value", "Unknown"))
            elif key == "popular_threat_category" and isinstance(value, list):
                for item in value:
                    categories.add(item.get("value", "Unknown"))

        print(f"[+] Categories       : {colored(', '.join(categories), attrs=['bold'])}")
        print(f"[+] Labels           : {colored(', '.join(labels).replace('/', '', ''), attrs=['bold'])}")
        print(f"[+] Threat Names     : {colored(', '.join(threat_names), attrs=['bold'])}")
    
    # Get signature rule information from several API's
    @staticmethod        
    def define_ruleset(ruleset_output):
        rule_id, rule_name, description, author, source = [], [], [], [], []
        
        rules = []
        if not ruleset_output:
            print("[-] No Rules Found.")
            return
        
        for item in ruleset_output:
            rules.append(item)
            
        for item in rules:
            for key, value in item.items():
                if key == "ruleset_id":
                    rule_id.append(value)
                elif key == "rule_name":
                    rule_name.append(value)
                elif key == "description":
                    description.append(value)
                elif key == "author":
                    author.append(value)
                elif key == "source":
                    source.append(value)
        
        for element in range(len(rule_id)):
            print(f"[+] Rule ID        : {colored(rule_id[element], attrs=['bold'])}")
            print(f"      - Rule Name      : {rule_name[element]}")
            print(f"      - Description    : {description[element]}")
            print(f"      - Author         : {author[element]}")
            print(f"      - Source         : {source[element]}")
    
    # Main Function        
    def parse_API_output(self, output):
        choice = self.choice
            
        print("Scan Overview: ")
        if choice == "files":
            print(f"[+] File Size        : {output.size} bytes")
            print(f"[+] File SHA256 Hash : {output.sha256}")
            print(f"[+] File Type        : {output.type_tag}")
            
            print("\nDetailed Crowdsourced Output:")     
            try:  
                self.define_ruleset(output.crowdsourced_yara_results)
            except:
                print("[-] No Yara Rules Found.")
            
            try:
                self.classify_threat(output.popular_threat_classification)
            except:
                print("[-] No Threat Classifications Found.")
        elif choice == "  ":
            self.rescan_url() # Submit the URL for re-analysis to ensure an output
            print(f"[+] Times URL Got Scanned : {output.times_submitted}")
            
            print("\nTotal Community Votes:")
            print(f"[+] Malicious Rating  : Score of {output.total_votes.get('malicious', 'None Found')}")
            print(f"[+] Harmless  Rating  : Score of {output.total_votes.get('harmless', 'None Found')}")

        print(f"\n{choice.capitalize()} Community Repudation: ")
        score = self.score_verdict(output.reputation)
        if score:
            print(f"[+] Identified as : {self.score_verdict(output.reputation)}")
        else:
            print("[-] No Score Found.")
        
        print("\nSummary of the most recent analysis:")
        for key, value in output.last_analysis_stats.items():
            print(f"[+] {key.capitalize():<20} : {'None' if value == 0 else value} found")
            
        if choice == "files":
            print("\nMITRE ATT&CK Technique's Identified (Displaying Max 15):")
            self.extract_behaviour_techniques_of_file()
        elif choice == "urls":
            print("\nAlternative Names Found:")
            self.find_alternative_names()

        print("\nDetailed results from individual antivirus engines:")    
        av_results = output.last_analysis_results
        for index, (key, value) in enumerate(av_results.items()):
            if index >= 15: break
            category = value.get("category", "Uncategorised")
            print(f"[+] Vendor : {key.capitalize():<20} -> Category : {colored('Malicious', 'red') if category == 'malicious' else category.capitalize()}\tType : {value.get('result'.capitalize(), 'Unknown')}")
        
        print("\n[+] User Comments (Verify Thoroughly): ")
        self.extract_comments()
        
        print(f"Final Scan Verdict {colored('(Please do not consider the below as definitive)', 'yellow')}:")
        self.final_verdict(av_results)

    # Send and get response
    def send_api_request_using_requests(self, api_param):
        API_KEY = self.API_KEY
        
        # Using v3 as v2 is depreciated
        url = f"https://www.virustotal.com/api/v3/{api_param}"
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return "not_status_200"

    # Extract community comments
    def extract_comments(self):  
        choice = self.choice
        data = self.data
             
        output = self.send_api_request_using_requests(f"{choice}/{data}/comments?limit=3")
        if output == "not_status_200" or output is None:
            print("[-] Unable to extract user comments, The community may have submitted nothing.\n")
            return
        
        try:
            comment_number = 1
            for elements in range(len(output.get("data", ""))):
                comments = ((output.get("data", [])[elements]).get("attributes", "").get("text", ""))
                if len(comments) > 700 : continue # Prevent Screen Clutter
                
                # Data Extracted
                comments = comments.replace("[/b]", "").replace("[b]", "")
                
                print("\t",colored(f'> Comment {comment_number} :', attrs=['bold']))
                print("\n".join([f"\t{line}" for line in comments.splitlines()]))
                print() # Add spacing
                
                comment_number += 1
        except (KeyError, TypeError):
            return

    # Extract behaviour analysis information
    def extract_behaviour_techniques_of_file(self):    
        data = self.data
            
        output = self.send_api_request_using_requests(f"files/{data}/behaviour_summary")
        if output == "not_status_200" or output is None:
            print("[-] Unable to extract file behaviour data.")
            return
        
        try:
            techniques = output.get("data", "").get("attack_techniques", [])    
        except (KeyError, TypeError):
            print("[-] Unable to extract MITRE Techniques")
            return
        
        for index, technique in enumerate(techniques):   
            if index == 15: break
            
            desciption = (techniques.get(technique, [])[0].get("description", "None Found")).capitalize()
            print(f"[+] Technique ID : {technique:<15} | Description : {desciption}")

    # Rescan URL if any fail arises
    def rescan_url(self):
        data = quote(self.data, safe='')
        
        # May not always work, but if it does, a re-scan will be submitted
        self.send_api_request_using_requests(f"urls/{data}/analyse")

    # Extract domain from link - if not already
    @staticmethod
    def extract_domain(data):
        if "https" in data or "http" in data:
            data = urlparse(data).netloc
            if data.startswith("www.") : data = data[4:]
        
        return data

    # Identify alternative names of the file sample    
    def find_alternative_names(self):
        data = self.extract_domain(self.data)
        
        output = self.send_api_request_using_requests(f"domains/{data}")
        if output == "not_status_200" or output is None:
            print("[-] Unable to extract domain information.")
            return
        
        # Extracting the subject alternative names from the last_https_certificate
        try:
            last_https_certificate = output.get("data", {}).get("attributes", {}).get("last_https_certificate", {})
            subject_alternative_names = last_https_certificate.get("extensions", {}).get("subject_alternative_name", [])
        except (KeyError, TypeError):
            print("[-] No subject alternative names found.")
            return
        
        if subject_alternative_names:
            for index , name in enumerate(subject_alternative_names):
                if index > 15 : break
                print(f"[+] {name}")
        else:
            print("[-] No subject alternative names found.")
