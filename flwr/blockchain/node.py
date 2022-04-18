import subprocess
from pathlib import Path

def start_node(config):

    network_Id = config['network_Id']
    sync_mode = config['sync_mode']
    threads = config['threads']
    gasprice = config['gasprice']
    
    bootnode_key_path = config['bootnode_key_path']
    bootnode_address = config['bootnode_address']
    
    data_dir = config['data_dir']
    account = config['account']
    password_path = config['password_path']
    
    http_port = config['http_port']
    ws_port = config['ws_port']
    listen_port = config['listen_port']

    mine = config['mine']

    cmd = (
        f"geth "
        f"{'--mine' if mine else ''} "
        f"--miner.threads={threads} --miner.gasprice={gasprice} --syncmode {sync_mode} --networkid {network_Id} "
        f"--bootnodes enode://`bootnode -writeaddress --nodekey={bootnode_key_path}`@{bootnode_address} "
        f"--datadir {data_dir} --unlock {account} --password {password_path} "
        f"--http --http.addr 0.0.0.0 --http.port {http_port} --http.corsdomain '*' --http.api 'admin,eth,net,web3,personal,miner' "
        f"--ws --ws.addr 0.0.0.0 --ws.port {ws_port} --ws.origins '*' --ws.api 'eth,net,web3' --port {listen_port} "
        f"--nousb --allow-insecure-unlock "
    )
    print(cmd)
    # read config
    # network_Id = config['network_Id']
    # sync_mode = config['sync_mode']
    # bootnode_ip = config['bootnode_ip']
    # account = config['account']
    # global_id = config['global_id']
    # actor_id = config['actor_id']
    # actor = config['actor']

    # abs_path = Path(__file__).parent.absolute()
    # data_dir = "%s/../accounts/%s%d/data" % (abs_path, actor, actor_id)
    # config_dir = "%s/../config" % abs_path
    # http_port = 8545 + (global_id) * 2
    # ws_port = 8546 + (global_id) * 2
    # port = 30303 + global_id
    # cmd = "geth --mine --miner.threads=4 --miner.gasprice=0 --syncmode %s --networkid %d \
    # --bootnodes enode://`bootnode -writeaddress --nodekey=%s/boot.key`@%s:30301 --datadir %s  \
    # --unlock %s --password %s/password.txt --http --http.addr 0.0.0.0 --http.port %d \
    # --http.corsdomain '*' --http.api 'admin,eth,net,web3,personal,miner' \
    # --ws --ws.addr 0.0.0.0 --ws.port %d --ws.origins '*' --ws.api 'eth,net,web3' --port %d \
    # --nousb --allow-insecure-unlock" % (sync_mode, network_Id, config_dir, bootnode_ip, data_dir, account, config_dir, http_port, ws_port, port)

    

    # p = subprocess.Popen(cmd, shell=True)
    # p.wait()
    
def check_node_config(config) -> None:
    assert config["actor"] in [1]
    assert "network_Id" in config
    assert "sync_mode" in config
    assert "threads" in config
    assert "gasprice" in config
    assert "bootnode_key_path" in config
    assert "bootnode_address" in config
    assert "data_dir" in config
    assert "account" in config
    assert "private_key" in config
    assert "password_path" in config
    assert "http_port" in config
    assert "ws_port" in config
    assert "listen_port" in config
    if "mine" in config:
        if config["mine"] == True:
            assert config["sync_mode"] == "full"
    else:
        config["mine"] == False