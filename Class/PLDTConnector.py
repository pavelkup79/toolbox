from UnixConnector import *

host='1.1.1.1 '
username='somepassword'
password='asomeuser'
port=2214
keyfile_path = 'private_key_file'
WAIT_TIME=10
SPA_log_path='cat /export/home/arbor/WKP_EAP-7.1.0/SPA.log* |  grep -A 2 -B 2 -e "FATAL" -e "ERROR" -e "ORA-" -e "Exception" -e "failed" | sort -n |tail -50;'



if __name__ == "__main__":
  execute_ssh_transport_command(host, port, username, password, None, None, SPA_log_path)