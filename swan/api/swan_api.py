import logging
import traceback
import json

from swan.api_client import APIClient
from swan.common.constant import *
from swan.object import HardwareConfig, LagrangeSpace
from swan.common.exception import SwanAPIException

class SwanAPI(APIClient):
  
    def __init__(self, api_key: str, login: bool = True, environment: str = None):
        """Initialize user configuration and login.

        Args:
            api_key: SwanHub API key, generated through website
            login: Login into Swanhub or Not
            environment: Selected server 'production/calibration'
        """
        self.token = None
        self.api_key = api_key
        self.environment = environment
        if environment == None:
            self.swan_url = SWAN_API
        else:
            self.swan_url = environment
        if login:
            self.api_key_login()

    def api_key_login(self):
        """Login with SwanHub API Key.

        Returns:
            A str access token for further SwanHub API access in
            current session.
        """
        params = {"api_key": self.api_key}
        try:
            result = self._request_with_params(
                POST, SWAN_APIKEY_LOGIN, self.swan_url, params, None, None
            )
            if result["status"] == "failed":
                raise SwanAPIException("Login Failed")
            self.token = result["data"] 
            logging.info("Login Successfully!")
        except SwanAPIException as e:
            logging.error(e.message)
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
              
    def get_hardware_config(self):
        """Query current hardware list object.
        
        Returns:
            list of HardwareConfig object.
            e.g. obj.to_dict() -> 
            {
                'id': 0, 
                'name': 'C1ae.small', 
                'description': 'CPU only · 2 vCPU · 2 GiB', 
                'type': 'CPU', 
                'reigion': ['North Carolina-US'], 
                'price': '0.0', 
                'status': 'available'
            }
        """
        try:
            response = self._request_without_params(GET, GET_CP_CONFIG, self.swan_url, self.token)
            self.all_hardware = [HardwareConfig(hardware) for hardware in response["data"]["hardware"]]
            return self.all_hardware
        except Exception:
            logging.error("Failed to fetch hardware configurations.")
            return None
        
    def deploy_task(self, cfg_name: str, region: str, start_in: int, duration: int, job_source_uri: str, wallet_address: str, tx_hash: str, paid: float = 0.0):
        """Sent deploy task request via orchestrator.

        Args:
            cfg_name: name of cp/hardware configuration set.
            region: region of hardware.
            start_in: unix timestamp of starting time.
            duration: duration of service runtime in unix time.
            job_source_uri: source uri for space.
            wallet_address: user wallet address.
            tx_hash: payment tx_hash swan payment contract.
            paid: paid amount in Eth.

        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            if self._verify_hardware_region(cfg_name, region):
                params = {
                    "paid": paid,
                    "duration": duration,
                    "cfg_name": cfg_name,
                    "region": region,
                    "start_in": start_in,
                    "wallet": wallet_address,
                    "tx_hash": tx_hash,
                    "job_source_uri": job_source_uri
                }
                result = self._request_with_params(POST, DEPLOY_TASK, self.swan_url, params, self.token, None)
                return result
            else:
                raise SwanAPIException(f"No {cfg_name} machine in {region}.")
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
        
    def get_deployment_info_json(self, task_uuid: str, file_path: str):
        """Retrieve deployment info of a deployed space with task_uuid.

        Args:
            task_uuid: uuid of space task, in deployment response.

        Returns:
            Deployment info.
        """
        try:
            response = self._request_without_params(GET, DEPLOYMENT_INFO+task_uuid, self.swan_url, self.token)
            with open(file_path, 'w') as f:
                json.dump(response, f, indent=2)
            return True
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return False
        
    def get_deployment_info(self, task_uuid: str):
        """Retrieve deployment info of a deployed space with task_uuid.

        Args:
            task_uuid: uuid of space task, in deployment response.

        Returns:
            Deployment info.
        """
        try:
            response = self._request_without_params(GET, DEPLOYMENT_INFO+task_uuid, self.swan_url, self.token)
            return response
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def get_real_url(self, task_uuid: str):
        deployment_info = self.get_deployment_info(task_uuid)
        try:
            jobs = deployment_info['data']['jobs']
            deployed_url = []
            for job in jobs:
                try:
                    if job['job_real_uri']:
                        deployed_url.append(job['job_real_uri'])
                except:
                    continue
            return deployed_url
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def get_payment_info(self):
        """Retrieve payment information from the orchestrator after making the payment.
        """
        try:
            payment_info = self._request_without_params(
                GET, PROVIDER_PAYMENTS, self.swan_url, self.token
            )
            return payment_info
        except:
            logging.error("An error occurred while executing get_payment_info()")
            return None

    def _verify_hardware_region(self, hardware_name: str, region: str):
        """Verify if the hardware exist in given region.

        Args:
            hardware_name: cfg name
            region: geological regions.

        Returns:
            True when hardware exist in given region.
            False when hardware does not exist or do not exit in given region.
        """
        if region == "Global":
            return True
        hardwares = self.get_hardware_config()
        for hardware in hardwares:
            if hardware.name == hardware_name:
                if region in hardware.region:
                    return True
                return False
        return False
