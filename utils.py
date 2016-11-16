import ConfigParser
import datetime
import httplib2
import json

from keystoneauth1 import exceptions
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as nova

config = ConfigParser.ConfigParser()
config.read('/etc/reconcile.conf')

def _get(url):
    h = httplib2.Http()
    resp, content = h.request(url, 'GET')

    if content:
        content = json.loads(content)
    return (resp, content)

class IpInfoCorrelator():
    nova_client = None
    contrail_url = ''
    contrail_vmis = '/virtual-machine-interfaces'

    def __init__(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=config.get('COMMON', 'os_auth_url'),
            username=config.get('COMMON', 'os_username'),
            password=config.get('COMMON', 'os_password'),
            user_domain_name=config.get('COMMON', 'os_user_domain_name'),
            project_name=config.get('COMMON', 'os_project_name'),
            project_domain_name=config.get('COMMON', 'os_project_domain_name'))

        sess = session.Session(auth=auth)

        self.nova_client = nova.Client(
            '2',
            session=sess,
            region_name=config.get('COMMON', 'os_region'))

    def __add_ips_to_instance(self, instance, vmi):
        if 'instance_ip_back_refs' in vmi and isinstance(vmi['instance_ip_back_refs'], list):
            if not hasattr(instance, 'fixed_ips'):
                instance.fixed_ips = []
            for fixed_ip in vmi['instance_ip_back_refs']:
                resp, content = None, None
                try:
                    resp, content = _get(fixed_ip['href'])
                except Exception as e:
                    error_dict = {'error': str(e)}
                    print("Contrail API failed to get details for fixed IP %(uuid)s: "
                          "Error: %(error)s" %
                          {'uuid': fixed_ip['uuid'], 'error': error_dict})
                    continue
                if 'status' not in resp or resp['status'] not in ['200']:
                    print("Got an error code from Contrail for fixed IP %(uuid)s" %
                          fixed_ip['uuid'])
                else:
                    instance.fixed_ips.append(content['instance-ip']['instance_ip_address'])

        if 'floating_ip_back_refs' in vmi and isinstance(vmi['floating_ip_back_refs'], list):
            if not hasattr(instance, 'floating_ips'):
                instance.floating_ips = []
            for floating_ip in vmi['floating_ip_back_refs']:
                resp, content = None, None
                try:
                    resp, content = _get(floating_ip['href'])
                except Exception as e:
                    error_dict = {'error': str(e)}
                    print("Contrail API failed to get details for floating IP %(uuid)s: "
                          "Error: %(error)s" %
                          {'uuid': floating_ip['uuid'], 'error': error_dict})
                    continue
                if 'status' not in resp or resp['status'] not in ['200']:
                    print("Got an error code from Contrail for floating IP %(uuid)s" %
                          floating_ip['uuid'])
                else:
                    instance.floating_ips.append(content['floating-ip']['floating_ip_address'])

    def get_ip_info(self):
        instances = self.nova_client.servers.list(search_opts={'all_tenants': 1})

        url = self.contrail_url + self.contrail_vmis
        resp, content = None, None
        try:
            resp, content = _get(url)
        except Exception as e:
            error_dict = {'error': str(e)}
            print("Contrail API failed to get VMIs: "
                  "Error: %(error)s" % error_dict)
        if 'status' not in resp or resp['status'] not in ['200']:
            print("Got an error code from Contrail VMI API")
            return None

        vmis = content['virtual-machine-interfaces']
        vmis_dict = {}
        for vmi in vmis:
            resp, content = None, None
            try:
                resp, content = _get(vmi['href'])
            except Exception as e:
                error_dict = {'error': str(e)}
                print("Contrail API failed to get details for VMI %(uuid)s: "
                      "Error: %(error)s" %
                      {'uuid': vmi['uuid'], 'error': error_dict})
                continue
            if 'status' not in resp or resp['status'] not in ['200']:
                print("Got an error code from Contrail for VMI %(uuid)s" %
                      vmi['uuid'])
            else:
                vmi_details = content['virtual-machine-interface']
                if 'virtual_machine_refs' in vmi_details and isinstance(vmi_details['virtual_machine_refs'], list):
                    for vmr in vmi_details['virtual_machine_refs']:
                        if vmr['uuid'] not in vmis_dict:
                            vmis_dict[vmr['uuid']] = []
                        vmis_dict[vmr['uuid']].append(vmi_details)

        for instance in instances:
            if instance.id in vmis_dict:
                for vmi in vmis_dict[instance.id]:
                    self.__add_ips_to_instance(instance, vmi)
        
        return instances
