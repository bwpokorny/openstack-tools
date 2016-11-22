import httplib2
import json
import mox
import unittest

import test_data
import utils

from keystoneauth1.loading._plugins.identity.generic import Password
from keystoneauth1 import session
from novaclient import client as nova
from urlparse import urljoin

class TestCase(unittest.TestCase):

    def setUp(self):
        self.m = mox.Mox()
        self.m.StubOutWithMock(utils.config, 'get')
        utils.config.get(
            'CONTRAIL', 'contrail_url').AndReturn(test_data.contrail_url)
        utils.config.get(
            'COMMON', 'os_auth_url').AndReturn(test_data.os_auth_url)
        utils.config.get(
            'COMMON', 'os_username').AndReturn(test_data.os_username)
        utils.config.get(
            'COMMON', 'os_password').AndReturn(test_data.os_password)
        utils.config.get(
            'COMMON', 'os_user_domain_name').AndReturn(test_data.os_user_domain_name)
        utils.config.get(
            'COMMON', 'os_project_name').AndReturn(test_data.os_project_name)
        utils.config.get(
            'COMMON', 'os_project_domain_name').AndReturn(test_data.os_project_domain_name)
        utils.config.get(
            'COMMON', 'os_region').AndReturn(test_data.os_region)
        self.m.StubOutWithMock(Password, 'load_from_options')
        self.mock_password = self.m.CreateMock(Password)
        Password.load_from_options(auth_url=mox.IgnoreArg(), password=mox.IgnoreArg(),
                                   project_domain_name=mox.IgnoreArg(),
                                   project_name=mox.IgnoreArg(), user_domain_name=mox.IgnoreArg(),
                                   username=mox.IgnoreArg()
                                  ).AndReturn(self.mock_password)

        self.m.StubOutWithMock(session, 'Session')
        session.Session(auth=self.mock_password).AndReturn(None)
        self.m.StubOutWithMock(nova, 'Client')
        self.mock_nova_client = mox.MockAnything()
        nova.Client(mox.IgnoreArg(), session=mox.IgnoreArg(), region_name=mox.IgnoreArg()
                   ).AndReturn(self.mock_nova_client)

        self.m.ReplayAll()
        self.ipinfo = utils.IpInfoCorrelator()
        self.m.VerifyAll()
        self.m.UnsetStubs()

        # Set up mock instance for individual test case
        self.m.StubOutWithMock(httplib2, 'Http')
        self.mock_http = self.m.CreateMock(httplib2.Http)
        self.m.StubOutWithMock(self.ipinfo.nova_client, 'servers')
        self.m.StubOutWithMock(self.ipinfo.nova_client.servers, 'list')

    def test_get(self):
        httplib2.Http().AndReturn(self.mock_http)
        self.mock_http.request(test_data.contrail_url, 'GET').AndReturn(
                               [test_data.basic_resp, test_data.basic_content])
        self.m.ReplayAll()
        ret_resp, ret_content = utils._get(test_data.contrail_url)
        self.assertEqual(ret_resp, test_data.basic_resp)
        self.assertEqual(ret_content, test_data.basic_content)
        self.m.VerifyAll()
        self.m.UnsetStubs()

    def test_get_ip_info(self):
        self.ipinfo.nova_client.servers.list(search_opts=mox.IgnoreArg()
                                            ).AndReturn(test_data.instances)
        url = urljoin(self.ipinfo.contrail_url, self.ipinfo.contrail_vmi_path)
        httplib2.Http().AndReturn(self.mock_http)
        self.mock_http.request(url, 'GET').AndReturn(
            [test_data.basic_resp,
             json.dumps({'virtual-machine-interfaces':
                        test_data.virtual_machine_interfaces})])
        for i in xrange(len(test_data.virtual_machine_interfaces)):
            httplib2.Http().AndReturn(self.mock_http)
            self.mock_http.request(
                     test_data.virtual_machine_interfaces[i]['href'], 'GET'
                     ).AndReturn(
                [test_data.basic_resp,
                 json.dumps({'virtual-machine-interface':
                  test_data.virtual_machine_interfaces[i]})])
        for i in xrange(len(test_data.virtual_machine_interfaces)):
            iipbr_len = 0
            if 'instance_ip_back_refs' in test_data.virtual_machine_interfaces[i]:
                iipbr_len = len(test_data.virtual_machine_interfaces[i]['instance_ip_back_refs'])
            for j in xrange(iipbr_len):
                httplib2.Http().AndReturn(self.mock_http)
                self.mock_http.request(
                    test_data.virtual_machine_interfaces[i]['instance_ip_back_refs'][j]['href'], 'GET').AndReturn(
                    [test_data.basic_resp,
                     json.dumps({'instance-ip':
                      test_data.virtual_machine_interfaces[i]['instance_ip_back_refs'][j]})])
            fipbr_len = 0
            if 'floating_ip_back_refs' in test_data.virtual_machine_interfaces[i]:
                fipbr_len = len(test_data.virtual_machine_interfaces[i]['floating_ip_back_refs'])
            for j in xrange(fipbr_len):
                httplib2.Http().AndReturn(self.mock_http)
                self.mock_http.request(test_data.virtual_machine_interfaces[i]['floating_ip_back_refs'][j]['href'], 'GET').AndReturn(
                    [test_data.basic_resp,
                     json.dumps({'floating-ip':
                      test_data.virtual_machine_interfaces[i]['floating_ip_back_refs'][j]})])

        self.m.ReplayAll()
        instances = self.ipinfo.get_ip_info()
        self.assertEqual(2, len(instances))
        self.assertEqual(2, len(instances[0].fixed_ips))
        self.assertEqual(2, len(instances[0].floating_ips))
        self.assertFalse(hasattr(instances[1], 'fixed_ips'))
        self.assertFalse(hasattr(instances[1], 'floating_ips'))
        self.m.VerifyAll()
        self.m.UnsetStubs()

        del instances[0].fixed_ips
        del instances[0].floating_ips

    def test_get_ip_info_vmi_conn_error(self):
        self.ipinfo.nova_client.servers.list(search_opts=mox.IgnoreArg()
                                            ).AndReturn(test_data.instances)
        url = urljoin(self.ipinfo.contrail_url, self.ipinfo.contrail_vmi_path)
        httplib2.Http().AndReturn(self.mock_http)
        self.mock_http.request(url, 'GET').AndRaise(httplib2.HttpLib2Error())

        self.m.ReplayAll()
        instances = self.ipinfo.get_ip_info()
        self.assertEqual(2, len(instances))
        for instance in instances:
            self.assertFalse(hasattr(instance, 'fixed_ips'))
            self.assertFalse(hasattr(instance, 'floating_ips'))
        self.m.VerifyAll()
        self.m.UnsetStubs()

    def test_get_ip_info_vmi_error_code(self):
        self.ipinfo.nova_client.servers.list(search_opts=mox.IgnoreArg()
                                            ).AndReturn(test_data.instances)
        url = urljoin(self.ipinfo.contrail_url, self.ipinfo.contrail_vmi_path)
        httplib2.Http().AndReturn(self.mock_http)
        self.mock_http.request(url, 'GET').AndReturn(
            [test_data.error_resp,
             None])

        self.m.ReplayAll()
        instances = self.ipinfo.get_ip_info()
        self.assertEqual(2, len(instances))
        for instance in instances:
            self.assertFalse(hasattr(instance, 'fixed_ips'))
            self.assertFalse(hasattr(instance, 'floating_ips'))
        self.m.VerifyAll()
        self.m.UnsetStubs()
