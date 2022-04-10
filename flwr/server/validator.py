# validator.py
from typing import Dict, List, Optional, Tuple
from flwr.server.strategy import FedAvg, Strategy
from flwr.server.client_proxy import ClientProxy
from flwr.common import (
    FitRes,
    Parameters,
    Scalar,
)
from py.flwr.common import parameter

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

    def set_client_weights(self, 
        rnd: int,
        results: List[Tuple[ClientProxy, FitRes]], 
        failures: List[BaseException]) -> None:

        # encode
        encoded_results = encode_parameter(results)

        # send transaction
        # set_clients_weights(encoded_results)
        nonce = self.w3.eth.get_transaction_count(self.contract_address)
        transaction = self.contract.functions.set_clients_weights(
            encoded_results).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'from': self.account,
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.signTransaction(transaction, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get global weight
    def handle_event(self, event):
        receipt = self.w3.eth.waitForTransactionReceipt(event['transactionHash'])
        result = self.contract.events.vvv.processReceipt(receipt)
        rnd = result[0]['args'] # round
        state = result[0]['args'] # aggregate state
        if state == True:
            global_parameter = self.get_global_weights_info() # encoded parameter
            results: List[Tuple[Optional[ClientProxy], FitRes]] = to_fit_res_list(global_parameter,self.strategy.min_fit_clients)

    def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
                time.sleep(poll_interval)

    def listen_aggregate_finish_event(self) -> None:
        block_filter = self.w3.eth.filter({'fromBlock':'latest', 'address':self.contract_address})
        self.log_loop(block_filter, 2)

    def get_global_weights_info(self):
        parameter = self.contract.functions.get_global_weights().call()
        return parameter

def decode_parameter(parameter: str) -> Parameter:

    # decode 
    base64_bytes = base64_string.encode("ascii")
    result_bytes = base64.b64decode(base64_bytes)
    result_string = result_bytes.decode("ascii")

    # turn to Optional[Weights] type
    
    return Parameters

def encode_parameter(parameters: Parameters) -> str:
    # encode
    parameters_bytes = str(parameters).encode("ascii")
    base64_bytes = base64.b64encode(parameters_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def to_fit_res_list(parameter, number_clients) -> List[Tuple[Optional[ClientProxy], FitRes]]:
    fitRes: FitRes
    fitRes.parameter = decode_parameter(parameter)

    results: List[Tuple[Optional[ClientProxy], FitRes]] = [fitRes.parameter for i in range(number_clients)]
    return results