import subprocess
from pathlib import Path

def start_node(config):
    # read config
    network_Id = config['network_Id']
    sync_mode = config['sync_mode']
    bootnode_ip = config['bootnode_ip']
    account = config['account']
    global_id = config['global_id']
    actor_id = config['actor_id']
    actor = config['actor']

    abs_path = Path(__file__).parent.absolute()
    data_dir = "%s/../accounts/%s%d/data" % (abs_path, actor, actor_id)
    config_dir = "%s/../config" % abs_path
    http_port = 8545 + (global_id) * 2
    ws_port = 8546 + (global_id) * 2
    port = 30303 + global_id
    cmd = "geth --mine --miner.threads=4 --miner.gasprice=0 --syncmode %s --networkid %d \
    --bootnodes enode://`bootnode -writeaddress --nodekey=%s/boot.key`@%s:30301 --datadir %s  \
    --unlock %s --password %s/password.txt --http --http.addr 0.0.0.0 --http.port %d \
    --http.corsdomain '*' --http.api 'admin,eth,net,web3,personal,miner' \
    --ws --ws.addr 0.0.0.0 --ws.port %d --ws.origins '*' --ws.api 'eth,net,web3' --port %d \
    --nousb --allow-insecure-unlock" % (sync_mode, network_Id, config_dir, bootnode_ip, data_dir, account, config_dir, http_port, ws_port, port)

    p = subprocess.Popen(cmd, shell=True)
    p.wait()

import json
if __name__ == "__main__":
    network_Id = 4321
    sync_mode = 'full'
    bootnode_ip = '127.0.0.1'
    abs_path = Path(__file__).parent.absolute()
    data_dir = "%s/../accounts/accounts.json" % abs_path
    f = open(data_dir)
    accounts = json.loads(f.read())

    actor = 'aggregator'
    global_id = 0 # modify 0,1
    actor_id = 0 # modify  0,1
    account = accounts[actor][actor_id] # modify

    config = {
        'network_Id': network_Id,
        'sync_mode': sync_mode,
        'bootnode_ip': bootnode_ip,
        'account': account,
        'global_id': global_id,
        'actor': actor,
        'actor_id': actor_id,
    }
    start_node(config)