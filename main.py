import zipfile
import json
from collections import defaultdict
import argparse
import os

def check_supported_auth(file_json):
    if file_json["services"][0]["configuration"]["security"]["type"] == "None":
        return ["Integration configuration is not using an authentication method"]
    return []

def check_no_token(endpoint):  
    for req_attr in ["queryParameters", "pathParameters", "headerParameters", "bodyParameters"]:
        for attr in endpoint[req_attr]:
            if "token" in attr["name"] or "bearer" in attr["name"]:
                return "Endpoint appears to implement a secret in plaintext"
    return None

def check_incremental_sync(endpoint):
    if "incrementalSyncQueryParameters" not in endpoint or len(endpoint["incrementalSyncQueryParameters"]) == 0:
        return "Endpoint does not use incremental syncs"
    return None

def check_pagination(endpoint):
    if "paginationMethod" not in endpoint:
        return "Endpoint does not use pagination"
    return None

def check_oauth_actions(file_json):
    if not file_json["supportsOAuthForActions"]:
        return ["Integration does not use OAuth for writeback actions"]
    return []

def check_endpoints(file_json):
    failures = defaultdict(list)
    for endpoint in file_json["services"][0]["configuration"]["dataEndpoints"]:
        pagination = check_pagination(endpoint)
        if pagination:
            failures[endpoint["name"]].append(pagination)
        incremental_sync = check_incremental_sync(endpoint)
        if incremental_sync:
            failures[endpoint["name"]].append(incremental_sync)
        no_token = check_no_token(endpoint)
        if no_token:
            failures[endpoint["name"]].append(no_token)
    return failures

def check_service_actions(file_json):
    failures = defaultdict(list)
    for sa in file_json["services"][0]["configuration"]["serviceActions"]:
        if sa['preActionDataUpdates'] == []:
            failures[sa['name']].append("Service action does not use update before action")
        if sa['postActionDataUpdates'] == []:
            failures[sa['name']].append("Service action does not use update after action")
    return failures

def generate_configuration_report(configuration_failures, results_file):
    results_file.write("#####################\nConfiguration report\n\n")
    if not configuration_failures:
        results_file.write("No configuration failures detected\n")
    else:
        results_file.write("Please provide a justification for any tests which have failed\n")
    for failure in configuration_failures:
        results_file.write("  {}\n".format(failure))
    results_file.write("\n")

def generate_endpoint_report(endpoint_failures, results_file):
    results_file.write("#####################\nEndpoint report\n\n")
    if not endpoint_failures:
        results_file.write("No endpoint failures detected\n")
    else:
        results_file.write("Please provide a justification for any tests which have failed\n")
    for k, v in endpoint_failures.items():
        results_file.write("\nEndpoint - {}\nHas the following failures:\n".format(k))
        for error in v:
            results_file.write("  {}\n".format(error))
    results_file.write("\n")

def generate_service_action_report(sa_failures, results_file):
    results_file.write("#####################\nService Action report\n\n")
    if not sa_failures:
        results_file.write("No service action failures detected\n")
    else:
        results_file.write("Please provide a justification for any tests which have failed\n")
    for k, v in sa_failures.items():
        results_file.write("\nService Action - {}\nHas the following failures:\n".format(k))
        for error in v:
            results_file.write("  {}\n".format(error))
    results_file.write("\n")

def main(mappFile):

    tempDir = 'tmp'
    with zipfile.ZipFile(mappFile, 'r') as zin:
        os.system('mkdir {}'.format(tempDir))
        zin.extractall(tempDir)

    configuration_failures = []

    with open("tmp/metadata.json", "r") as metadata:
        metadata_json = json.load(metadata)
        configuration_failures.extend(check_oauth_actions(metadata_json))

    with open("tmp/file.sapp", "r") as metadata:
        file_json = json.load(metadata)

        configuration_failures.extend(check_supported_auth(file_json))
        endpoint_failures = check_endpoints(file_json)
        sa_failures = check_service_actions(file_json)

    output_file = "results.txt"
    with open(output_file, "w") as results_file:
        generate_configuration_report(configuration_failures, results_file)
        generate_endpoint_report(endpoint_failures, results_file)
        generate_service_action_report(sa_failures, results_file)

    os.system('rm -rf {}'.format(tempDir))

if __name__ == "__main__":
    # python3 main.py --file ServiceNowHTTPnew.service.mapp
    parser = argparse.ArgumentParser(description='Test microapp bundle against best practices')
    parser.add_argument('--file', dest='mappFile', help='name and location of the mapp export file')

    args = parser.parse_args()
    main(args.mappFile)


