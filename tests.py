import mox
import unittest

import test_data
import utils

from keystoneauth1.loading._plugins.identity.generic import Password
from keystoneauth1 import session
from novaclient import client as nova
from neutronclient.neutron import client as neutron

class TestCase(unittest.TestCase):

    def setUp(self):
        self.m = mox.Mox()
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
        self.m.StubOutWithMock(neutron, 'Client')
        self.mock_neutron_client = mox.MockAnything()
        neutron.Client(mox.IgnoreArg(), session=mox.IgnoreArg(), region_name=mox.IgnoreArg()
                      ).AndReturn(self.mock_neutron_client)

        self.m.ReplayAll()
        self.ipinfo = utils.IpInfoCorrelator()
        self.m.VerifyAll()
        self.m.UnsetStubs()

        self.m.StubOutWithMock(self.ipinfo.nova_client, 'servers')
        self.m.StubOutWithMock(self.ipinfo.nova_client.servers, 'list')
        self.m.StubOutWithMock(self.ipinfo.neutron_client, 'list_ports')
        self.m.StubOutWithMock(self.ipinfo.neutron_client, 'list_floatingips')

    def test_get_ip_info(self):
        self.ipinfo.nova_client.servers.list(search_opts=mox.IgnoreArg()
                                            ).AndReturn(test_data.instances)
        self.ipinfo.neutron_client.list_ports().AndReturn({'ports': test_data.ports})
        self.ipinfo.neutron_client.list_floatingips().AndReturn({'floatingips': test_data.floatingips})

        self.m.ReplayAll()
        instances = self.ipinfo.get_ip_info()
        self.assertEqual(2, len(instances))
        self.assertEqual(1, len(instances[0].fixed_ips))
        self.assertEqual(2, len(instances[0].floating_ips))
        self.assertIsNone(instances[1].fixed_ips)
        self.m.VerifyAll()
