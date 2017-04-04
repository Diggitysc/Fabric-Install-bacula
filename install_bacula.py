import os
from fabric.api import *
from fabric.contrib.files import exists

HERE = os.path.abspath(os.path.dirname(__file__))

'''
Usage
python write_client_fd_conf <machine>
fab  -f install_bacula.py -I -H <machine> install_bacula

This script does not currently work for centos 7
'''


@parallel
def install_bacula():
    with cd('/etc/sysconfig/'):
        #return_stdout = sudo('grep 9102 iptables')
        line_number = sudo('grep -n "\--dport" iptables').split('\r\n')

        port_open = False
        rh_text = False
        for line in line_number:
            if "RH-Firewall" in line:
                rh_text = True
            if "--dport 9102" in line:
                print "Port 9102 is already open"
                port_open = True

        if not port_open:
            sudo('cp iptables iptables.bak')
            insert_point = line_number[-1].split(':')[0]
            insert_point = int(insert_point) + 1
            if rh_text:
                command = "sed -i '{0} i -A RH-Firewall-1-INPUT -m state --state NEW -m tcp -p tcp -s 192.168.111.220 --dport 9102 -j ACCEPT' iptables".format(insert_point)
            else:
                command = "sed -i '{0} i -A INPUT -m state --state NEW -m tcp -p tcp -s 192.168.111.220 --dport 9102 -j ACCEPT' iptables".format(insert_point)
            sudo(command)
            command = "sed -i '{0} i \# bacula' iptables".format(insert_point)
            sudo(command)
            sudo('service iptables restart')

    with cd('/etc/yum.repos.d'):
        sudo('wget https://repos.fedorapeople.org/repos/slaanesh/bacula7/epel-bacula7.repo')
        sudo('yum -y install bacula-client')
        put('bacula-fd.conf', '/etc/bacula/', use_sudo=True)
        sudo('service bacula-fd start')
