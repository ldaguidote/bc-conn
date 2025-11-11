import requests
import xml.etree.ElementTree as ET

class BCHandler:
    """Handler for BC API operations."""
    
    def __init__(self, tenant_id: str, env_name: str, endpoint_type: str, token: str):
        
        self.base_url = "https://api.businesscentral.dynamics.com/v2.0/"
        self.tenant_id = tenant_id
        self.env_name = env_name
        self.token = token
        self.headers = {'Authorization': f'Bearer {self.token}'}
        self.endpoint_type = endpoint_type
        self.set_endpoint_type(endpoint_type)

    def set_endpoint_type(self, type: str):
        """
        Set the API endpoint type for Business Central.
        
        Args:
            type: Type of endpoint ('ODataV4' or 'v2')
            
        Raises:
            ValueError: If the endpoint type is invalid
        """

        if type == 'ODataV4':
            self.endpoint_prefix = f"{self.base_url}{self.tenant_id}/{self.env_name}/ODataV4/"
        
        elif type == 'v2':
            self.endpoint_prefix = f"{self.base_url}{self.tenant_id}/{self.env_name}/api/v2.0/"

        else:
            raise ValueError("Invalid endpoint type. Choose 'ODataV4' or 'v2'.")

    def get_metadata(self):
        endpoint = self.endpoint_prefix + '$metadata'
        response = self._get(endpoint, json=False)
        metadata = BCMetaData(response)
        return metadata

    def get_companies(self):
        suffix = "Company" if self.endpoint_type == "ODataV4" else "companies"
        endpoint = self.endpoint_prefix + suffix
        response = self._get(endpoint)
        data = BCData(response)
        return data

    def get_data(self, company_name: str, table_name: str):
        """
        Retrieve data from a specified table in Business Central.
        
        Args:
            table_name: Name of the table to retrieve data from
            
        Returns:
            dict: Data retrieved from the specified table
            
        Raises:
            ValueError: If table name is invalid
            Exception: For other errors during data retrieval
        """
        if not table_name:
            raise ValueError("Table name is required")
        
        endpoint = self.endpoint_prefix + f"Company('{company_name}')/{table_name}"
        response = self._get(endpoint)
        return response

    def _get(self, endpoint: str, json=True):
        try:
            response = requests.get(endpoint, headers=self.headers, verify=False)  # Consider using proper SSL certificates in production
            response.raise_for_status()  # Raise exception for HTTP errors
            
            if json:
                return response.json()
            else:
                return response.content.decode('utf-8')
            
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to retrieve data: {e.response.status_code} - {e.response.text}")
        
        except Exception as e:
            raise Exception(f"An error occurred while retrieving data: {str(e)}")
        

class BCMetaData:

    def __init__(self, xml_metadata):
        self.raw = xml_metadata
        self._process_xml(self.raw)

    def _process_xml(self, xml_metadata):
        """
        Parse the xml metadata file from Business Central
        """

        ns = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm'
        }

        root = ET.fromstring(xml_metadata)

        entities = {}

        # Parse element tree into JSON
        for entity in root.findall('.//edm:EntityType', ns):
            entity_name = entity.attrib.get('Name')
            entities[entity_name] = {}

            for prop in entity.findall('edm:Property', ns):
                prop_name = prop.attrib.get('Name')
                prop_type = prop.attrib.get('Type')
                prop_null = prop.attrib.get('Nullable')
                prop_maxlen = prop.attrib.get('MaxLength')
                prop_scale = prop.attrib.get('Scale')

                annotations = {}
                for ann in prop.findall('edm:Annotation', ns):
                    term = ann.attrib.get('Term')
                    value = ann.attrib.get('String') or ann.attrib.get('Bool')
                    enum = ann.find('edm:EnumMember', ns)
                    if enum is not None:
                        value = enum.text
                    annotations[term] = value

                entities[entity_name][prop_name] = {
                    'Type': prop_type,
                    'Nullable': prop_null,
                    'MaxLength': prop_maxlen,
                    'Scale': prop_scale,
                    'Annotations': annotations
                }

        # Process JSON into flattened JSON that can be normalized
        rows = []

        for prop, info in entities.items():
            for field, details in info.items():
                row = {'API Endpoint Name': prop}
                row['Column Name'] = field
                row['DataType'] = details.get('Type', None)
                row['Nullable'] = details.get('Nullable', None)
                row['MaxLength'] = details.get('MaxLength', None)
                row['Scale'] = details.get('Scale', None)
                for k, v in details.get('Annotations', {}).items():
                    row[f'Annotations.{k}'] = v
                rows.append(row)

        self.json = entities
        self.flat_json = rows

class BCData:

    def __init__(self, json_data):
        self.raw = json_data
        self._process_data(self.raw)

    def _process_data(self, json_data):
        self.flat_json = json_data.get('value', [])