import web3
import logging
import os

from swan.api_client import APIClient
from swan.common.constant import *
from swan.object.cp_config import HardwareConfig


class SwanAPI(APIClient):

    def __init__(self, api_key: str):
        """Initialize Swan API connection with API key.

        Args:
            api_key: API key for swan services.
        """
        super().__init__(api_key)

    def get_hardware_config(self):
        """Query current hardware list.
        
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
            response = self._request_without_params(
                GET, GET_CP_CONFIG, SWAN_API, self.token
            )
            self.all_hardware = [HardwareConfig(hardware) for hardware in response["data"]["hardware"]]
            return self.all_hardware
        except Exception:
            logging.error("Failed to fetch hardware configurations.")
            return None
        
    def deploy_space(self, cfg_name: str, region: str, start_in: int, duration: int, job_source_uri: str, paid: int = 0.0):
        """Sent deploy space request via orchestrator.

        Args:
            cfg_name: name of cp/hardware configuration set.
            region: region of hardware.
            start_in: unix timestamp of starting time.
            duration: duration of service runtime in unix time.
            job_source_uri: source uri for space.

        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            params = {
                "paid": paid,
                "duration": duration,
                "cfg_name": cfg_name,
                "region": region,
                "start_in": start_in,
                "tx_hash": None,
                "job_source_uri": job_source_uri
            }
            result = self._request_with_params(
                POST, DEPLOY_SPACE, SWAN_API, params, self.token, None
            )
            return result
        except Exception:
            logging.error("")
            return None
        
    def get_deployment_info(self, task_uuid: str):
        """Retrieve deployment info of a deployed space with task_uuid.

        Args:
            task_uuid: uuid of space task, in deployment response.

        Returns:
            Deployment info.
        """
        try:
            params = {
                "task_uuid": task_uuid
            }
            response = self._request_with_params(
                GET, GET_CP_CONFIG, SWAN_API, params, self.token, None
            )
            return response
        except Exception:
            logging.error("")
            return None



    # def build_task(self, source_code_url, instance_type, task_name, public_key=None):
    #     """Prepare a task for deployment with the required details.
    #     - source_code_url: URL to the code repository containing Docker/K8s file and env file
    #     - instance_type: Type of instance needed for the task
    #     - task_name: A name for the task
    #     - public_key: Optional public key for accessing confidential data
    #     """
    #     try:
    #         params = {
    #             "source_code_url": source_code_url,
    #             "instance_type": instance_type,
    #             "task_name": task_name,
    #             "public_key": public_key,
    #         }
    #         result = self._request_with_params(
    #             POST, BUILD_TASK, self.orchestrator_url, params, self.token
    #         )
    #         return result
    #     except:
    #         logging.error("An error occurred while executing build_task()")
    #         return None

    # def propose_task(self):
    #     """Propose the prepared task to the orchestrator."""
    #     try:
    #         result = self._request_with_params(
    #             POST, TASKS, self.orchestrator_url, {}, self.token
    #         )
    #         return result
    #     except Exception as e:
    #         return None

    # def make_payment(self):
    #     """Make payment for the task build after acceptance by the orchestrator."""
    #     try:
    #         payment_info = self._request_without_params(
    #             GET, PAYMENT_INFO, self.orchestrator_url, self.token
    #         )
    #         payment_info["payment_key"] = self.payment_key
    #         result = self._request_with_params(
    #             POST,
    #             USER_PROVIDER_PAYMENTS,
    #             self.orchestrator_url,
    #             payment_info,
    #             self.token,
    #         )
    #         return result
    #     except:
    #         logging.error("An error occurred while executing make_payment()")
    #         return None

    # def get_payment_info(self):
    #     """Retrieve payment information from the orchestrator after making the payment."""
    #     try:
    #         payment_info = self._request_without_params(
    #             GET, PROVIDER_PAYMENTS, self.orchestrator_url, self.token
    #         )
    #         return payment_info
    #     except:
    #         logging.error("An error occurred while executing get_payment_info()")
    #         return None

    # def get_task_status(self):
    #     """Fetch the current status of the task from the orchestrator."""
    #     try:
    #         task_status = self._request_without_params(
    #             GET, DEPLOY_STATUS, self.orchestrator_url, self.token
    #         )
    #         return task_status
    #     except:
    #         logging.error("An error occurred while executing get_task_status()")
    #         return None

    # def fetch_task_details(self):
    #     """Retrieve the deployed URL and credentials/token for access after task success.
    #     Decrypt the credentials/token with the private key if necessary.
    #     """
    #     # PRIVATE KEY GIVEN THROUGH .ENV FILE
    #     private_key = os.environ.get("PRIVATE_KEY")
    #     try:
    #         task_details = self._request_without_params(
    #             GET, TASK_DETAILS, self.orchestrator_url, self.token
    #         )
    #         return task_details
    #     except:
    #         logging.error("An error occurred while executing fetch_task_details()")
    #         return None
