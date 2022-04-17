# aggregator.py
from typing import Dict, List, Optional
from flwr.server.strategy import FedAvg, Strategy
from flwr.common import (
    Scalar,
    Weights,
    weights_to_parameters,
    parametersList_to_fitResList
)

from flwr.common.parameter import decode_weights, encode_weights

from web3 import Web3
import time
import subprocess
from pathlib import Path

class Aggregator:
    def __init__(self, account: str, private_key: str, provider_url: str, contract_address: str, abi: Dict, strategy: Optional[Strategy] = None) -> None:
        self.account = account
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.strategy: Strategy = strategy if strategy is not None else FedAvg()
    
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

    def set_strategy(self, strategy: Strategy) -> None:
        """Replace server strategy."""
        self.strategy = strategy

    # aggregate
    def listen_aggregate_event(self) -> None:
        block_filter = self.w3.eth.filter({'fromBlock':'latest', 'address':self.contract_address})
        while True:
            for event in block_filter.get_new_entries():
                time.sleep(2)
                receipt = self.w3.eth.waitForTransactionReceipt(event['transactionHash'])
                result = self.contract.events.AggregateEvent.processReceipt(receipt)
                rnd = result[0]['id'] # round
                encoded_client_weights = result[0]['client_weights'] # client_weights
                # decode client weights
                client_weights = decode_weights(encoded_client_weights)
                client_parameters = [(weights_to_parameters(weights), num_examples) for weights, num_examples in client_weights]
                results = parametersList_to_fitResList(client_parameters)
                aggregated_weights = self.strategy.aggregate_fit(rnd, results, None)
                encoded_aggregated_weights = encode_weights(aggregated_weights)
                self.set_aggregated_weights(encoded_aggregated_weights)

    def set_aggregated_weights(self, weights: str) -> None:
        nonce = self.w3.eth.get_transaction_count(self.contract_address)
        transaction = self.contract.functions.set_aggregated_weights(
            weights).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'from': self.account,
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.signTransaction(transaction, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # tx_hash == signed_tx.hash if tx success
        # self.w3.eth.wait_for_transaction_receipt(signed_tx.hash)

    def get_unaggregated_info(self):
        parameters, num_examples = self.contract.functions.get().call()
        return parameters, num_examples