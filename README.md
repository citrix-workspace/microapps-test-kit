# Microapp Test Kit
This repository contains code to assist with the validation of Citrix microapp bundles, to ensure they comply with [best practices](https://developer.cloud.com/workspace-connector/integration-best-practices).

The test kit checks microapp bundles for the following conditions:

1. If pagination is configured for each endpoint
1. If incremental sync is configured for each endpoint
1. If OAuth2 is being used for write back actions
1. That no tokens or secrets are hardcoded in the endpoints
1. If update before/after action is configured for each service action

The test kit will then output a file called "results.txt" which provides details on any failed tests.

If you are submitting a microapp to Citrix Ready it is required that you run this script beforehand and provide justification for any failed tests (for example, an endpoint may not support pagination).

# Steps

1. [Export the microapp integration bundle](https://docs.citrix.com/en-us/citrix-microapps/export-import-microapp.html) from the microapp admin console
1. Copy the exported file into this directory
1. Run the script: `python3 main.py --file <file_name>.mapp`
1. View the results in "results.py"

For an example results file, see results_example.txt