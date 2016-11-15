import datetime

from keystoneauth1 import exceptions
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as nova
from neutronclient.neutron import client as neutron 

class IpInfoCorrelator():
    nova_client = None
    neutron_client = None
    ports_dict = {}
    floatingips_dict = {}

    def __init__(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
                           auth_url='',
                           username='',
                           password='',
                           user_domain_name='',
                           project_name='',
                           project_domain_name='')

        sess = session.Session(auth=auth)

        self.nova_client = nova.Client('2',
                           session=sess,
                           region_name='ash2')
        self.neutron_client = neutron.Client('2.0',
                           session=sess,
                           region_name='ash2')

    def __get_floatingips(self):
        floatingip_retries = 7
        floatingips = None
        while floatingip_retries > 0:
            try:
                now = datetime.datetime.now()
                print "====Trying====" + str(now)
                floatingips = self.neutron_client.list_floatingips()['floatingips']
                floatingip_retries = 0
            except exceptions.ConnectTimeout:
                now = datetime.datetime.now()
                print "====Exception===" + str(now)
                floatingip_retries -= 1
                if floatingip_retries < 1:
                    raise
        return floatingips

    def __add_ips_to_instance(self, instance):
        instance.fixed_ips = []
        for port in self.ports_dict[instance.id]:
            for fixed_ip in port['fixed_ips']:
                if fixed_ip['ip_address'] is not None:
                    instance.fixed_ips.append(fixed_ip['ip_address'])
            if port['id'] in self.floatingips_dict:
                instance.floating_ips = []
                for floating_ip in self.floatingips_dict[port['id']]:
                    if floating_ip['floating_ip_address'] is not None:
                        instance.floating_ips.append(floating_ip['floating_ip_address'])

    def get_ip_info(self):
        instances = self.nova_client.servers.list(search_opts={'all_tenants': 1})
        
        ports = self.neutron_client.list_ports()['ports']
        for port in ports:
            if port['device_id'] not in self.ports_dict:
                self.ports_dict[port['device_id']] = []
            self.ports_dict[port['device_id']].append(port)

        floatingips = self.__get_floatingips()
        for floatingip in floatingips:
            if floatingip['port_id'] not in self.floatingips_dict:
                self.floatingips_dict[floatingip['port_id']] = []
            self.floatingips_dict[floatingip['port_id']].append(floatingip)

        for instance in instances:
            if instance.id in self.ports_dict:
                self.__add_ips_to_instance(instance)

        return instances
