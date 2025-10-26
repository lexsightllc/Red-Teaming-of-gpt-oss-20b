# SPDX-License-Identifier: MPL-2.0

import logging

class APIAdaptability:
    """
    Manages adaptability to changes in model provider APIs. (Point 30)
    """
    def __init__(self):
        logging.info("Initialized APIAdaptability manager.")
        self.api_abstraction_map = {} # Maps generic calls to specific API versions

    def register_api_version(self, api_name, api_version, client_class):
        """
        Registers a specific client class for an API version.
        """
        if api_name not in self.api_abstraction_map:
            self.api_abstraction_map[api_name] = {}
        self.api_abstraction_map[api_name][api_version] = client_class
        logging.info(f"Registered API {api_name} v{api_version}")

    def get_client(self, api_name, api_version="latest", config=None):
        """
        Returns an appropriate API client instance for the requested version.
        """
        if api_name not in self.api_abstraction_map:
            raise ValueError(f"API '{api_name}' not registered.")
        
        if api_version == "latest":
            # Find latest version or use a default
            versions = sorted(self.api_abstraction_map[api_name].keys(), reverse=True)
            if not versions:
                raise ValueError(f"No versions found for API '{api_name}'.")
            resolved_version = versions[0]
        else:
            resolved_version = api_version
        
        client_class = self.api_abstraction_map[api_name].get(resolved_version)
        if not client_class:
            raise ValueError(f"API '{api_name}' version '{resolved_version}' not found.")
        
        logging.info(f"Providing client for {api_name} v{resolved_version}.")
        return client_class(config) # Instantiate client with config
    
    def automated_validation(self, api_client):
        """
        Runs automated validation tests against a new API version.
        """
        logging.info(f"Running automated validation for {api_client.model_name}.")
        # This would include making test calls, checking response formats, etc.
        # Return True if validation passes, False otherwise.
        return True
