import flwr as fl
import json
from pathlib import Path
# from flwr.blockchain.init_wallet import create_accounts_V2, BC_ACCOUNTS_PATH, BC_BOOTNODE_KEY_PATH

if __name__ == "__main__":
    
    # init wallet
    actors = ['validator']
    amounts = [1] 
    # create_accounts_V2()

    # data_dir = f"{BC_ACCOUNTS_PATH}/accounts.json"
    # f = open(data_dir)
    # accounts = json.loads(f.read())

    # actor = 'validator'
    
    # account = accounts[actor][1] # modify
    # # actor: validator -> 1
    # config = {
    #     'network_Id': 4321,
    #     'sync_mode': 'snap',
    #     'threads': 4,
    #     'gasprice': 0,
    #     'bootnode_key_path': "bb",
    #     'bootnode_address': "aa",
    #     'data_dir': "cc",
    #     'account': "0xss",
    #     'private_key': "0xss",
    #     'password_path': "zxc",
    #     'http_port': 123,
    #     'ws_port': 456,
    #     'listen_port': 678,
    #     'mine': True,
    #     'actor': 1,
    #     'num_rounds': 3
    # }
    # fl.server.start_server(config=config)
