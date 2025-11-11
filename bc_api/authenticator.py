import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

class BCTokenClient:
    """Client for retrieving BC tokens."""
    
    def __init__(self, base_url: str = "192.168.70.231:4413", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get_token(self, username: str, password: str) -> str:
        """
        Retrieve BC token using username and password.
        
        Args:
            username: User credentials
            password: User password
            
        Returns:
            str: Authentication token
            
        Raises:
            ValueError: If credentials are invalid
            ConnectionError: If network connection fails
            Exception: For other authentication errors
        """
        if not username or not password:
            raise ValueError("Username and password are required")
        
        endpoint = f'https://{username}:{password}@{self.base_url}/bcWT/Token'
        
        try:
            response = requests.get(
                endpoint, 
                verify=False,  # Consider using proper SSL certificates in production
                timeout=self.timeout
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            if 'token' not in data:
                raise Exception("Token not found in response")
            
            return data['token']
            
        except Timeout:
            raise ConnectionError("Request timed out. Please check your network connection.")
        
        except ConnectionError as e:
            raise ConnectionError("Failed to connect to server. Please check the server address and network connection.")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Please check your credentials.")
            else:
                raise Exception(f"Server error: {e.response.status_code}")
        
        except ValueError as e:
            raise Exception("Invalid response from server")
        
        except RequestException as e:
            raise Exception("Failed to retrieve token. Please check your credentials or network connection.")