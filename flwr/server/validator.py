# validator.py
from typing import Dict, List, Optional, Tuple
from flwr.server.strategy import FedAvg, Strategy
from flwr.server.client_proxy import ClientProxy
from flwr.common import (
    Weights,
    Scalar,
)
from flwr.common import parameter

from web3 import Web3
import time

class Validator:
    def __init__(self, account: str, private_key: str, provider_url: str, contract_address: str, abi: Dict, strategy: Optional[Strategy] = None) -> None:
        self.account = account
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        self.strategy: Strategy = strategy if strategy is not None else FedAvg()
    
    def set_strategy(self, strategy: Strategy) -> None:
        """Replace server strategy."""
        self.strategy = strategy

    # send transaction
    def set_client_weights(self, encode_weights: str) -> None:
        nonce = self.w3.eth.get_transaction_count(self.contract_address)
        transaction = self.contract.functions.set_clients_weights(
            encode_weights).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'from': self.account,
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.signTransaction(transaction, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    def listen_aggregate_finish_event(self) -> Tuple[int, str]:
        block_filter = self.w3.eth.filter({'fromBlock':'latest', 'address':self.contract_address})
        while True:
            for event in block_filter.get_new_entries():
                time.sleep(2)
                receipt = self.w3.eth.waitForTransactionReceipt(event['transactionHash'])
                result = self.contract.events.ValidateEvent.processReceipt(receipt)
                if result[0]:
                    rnd = result[0]['id'] # round
                    encoded_aggregated_weight = result[0]['aggregated_weight'] # aggregated weight
                    return rnd, encoded_aggregated_weight

    def get_aggregated_weights(self) -> str:
        encoded_aggregated_weights = self.contract.functions.get_aggregated_weights().call()
        return encoded_aggregated_weights
