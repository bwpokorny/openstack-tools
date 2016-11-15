class Server():
    def __init__(self, id):
        self.id = id
        self.fixed_ips = None
        self.floating_ips = None

instances = [Server('7ed7edf8-e5a7-4a04-92e0-725ab6f045f0'),
             Server('no-fip')]

ports = [
    {u'fixed_ips': [
        {u'subnet_id': u'2f657be2-de1a-4228-a553-9d82a14602be',
         u'ip_address': u'192.168.3.244'}],
     u'id': u'a22788b1-b928-4d03-bd7f-ad1e42f4b330',
     u'device_id': u'7ed7edf8-e5a7-4a04-92e0-725ab6f045f0'}]

floatingips = [
    {u'floating_ip_address': u'100.73.79.105',
     u'port_id': u'a22788b1-b928-4d03-bd7f-ad1e42f4b330',
     u'id': u'32c9ea7c-fed3-489b-ae36-6fba779d087a'},
    {u'floating_ip_address': u'100.73.76.168',
     u'port_id': None,
     u'id': u'c14ec16d-c0c6-4ab6-9c2a-e6bd68fd2943'},
    {u'floating_ip_address': u'100.73.96.131',
     u'port_id': u'a22788b1-b928-4d03-bd7f-ad1e42f4b330',
     u'id': u'57656ab5-2a16-4101-b650-16eb83f43c82'}]
