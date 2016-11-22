class Server():
    def __init__(self, id):
        self.id = id

os_username='user_one'
os_auth_url='https://keystone.domain.com/v3'
os_password='my_password'
os_user_domain_name='Domain1'
os_project_name='Project1'
os_project_domain_name='Domain1'
os_region='Region1'
contrail_url='http://contrail-web.domain.com:8082'

basic_resp = {'status': '200'}
basic_content = {}
error_resp = {'status': '404'}

instances = [Server('7ed7edf8-e5a7-4a04-92e0-725ab6f045f0'),
             Server('no-fip')]

virtual_machine_interfaces = [
    {"href": "http://contrail-web.domain.com:8082/virtual-machine-interface/c81e84b9-844c-4368-9760-2e241fb4a8f1",
     "uuid": "c81e84b9-844b-4368-9760-2e241fb4a8f1",
     "virtual_machine_refs": [
         {"href": "http://contrail-web.domain.com:8082/virtual-machine/7ed7edf8-e5a7-4a04-92e0-725ab6f045f0",
          "uuid": "7ed7edf8-e5a7-4a04-92e0-725ab6f045f0"}],
     "floating_ip_back_refs": [
         {"href": "http://contrail-web.domain.com:8082/floating-ip/4760508b-c7a8-43e0-a6a2-245d8f8c969b",
          "floating_ip_address": "100.73.96.213",
          "uuid": "4760508b-c7a8-43e0-a6a2-245d8f8c969b"},
         {"href": "http://contrail-web.domain.com:8082/floating-ip/c36a6188-bc19-4ac1-8892-44b92baf0b2f",
          "floating_ip_address": "100.73.96.214",
          "uuid": "c36a6188-bc19-4ac1-8892-44b92baf0b2f"}],
     "instance_ip_back_refs": [
         {"href": "http://contrail-web.domain.com:8082/instance-ip/23a82b14-555a-41be-ab5e-30bbc06c0ac6",
          "instance_ip_address": "192.168.3.3",
          "uuid": "23a82b14-555a-41be-ab5e-30bbc06c0ac6"},
         {"href": "http://contrail-web.domain.com:8082/instance-ip/663feb3c-ce4d-4067-9f20-8f7331f3535a",
          "instance_ip_address": "192.168.3.4",
          "uuid": "663feb3c-ce4d-4067-9f20-8f7331f3535a"}]},
    {"href": "http://contrail-web.domain.com:8082/virtual-machine-interface/b27d4f86-7ebc-4100-9538-1ab1941cf0d7",
     "uuid": "b27d4e86-7ebc-4100-9538-1ab1941cf0d7",
     "virtual_machine_refs": [
         {"href": "http://contrail-web.domain.com:8082/virtual-machine/7ed7edf8-e5a7-4a04-92e0-725ab6f045f0",
          "uuid": "7ed7edf8-e5a7-4a04-92e0-725ab6f045f0"}]},
    {"href": "http://contrail-web.domain.com:8082/virtual-machine-interface/980b23d1-a7db-4c16-a1a8-71a491dfc049",
     "uuid": "980b23d1-b7db-4c16-a1a8-71a491dfc049",
     "virtual_machine_refs": [
         {"href": "http://contrail-web.domain.com:8082/virtual-machine/247bbf74-9bb5-4264-9b6f-9df90599fd52",
          "uuid": "247bbf74-9bb5-4264-9b6f-9df90599fd52"}]}
]
