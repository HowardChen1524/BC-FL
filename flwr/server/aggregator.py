# aggregator.py
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

class Aggregator:
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

    def aggregate_fit(self,
        rnd: int,
        results: List[Tuple[Optional[ClientProxy], FitRes]],
        failures: Optional[List[BaseException]] = None,
        ) -> Tuple[
            Optional[Parameters],
            Dict[str, Scalar],
        ]:
        return self.strategy.aggregate_fit(rnd, results, failures)

    # def aggregate_evaluate(self) -> Tuple[
    #         Optional[float],
    #         Dict[str, Scalar],
    #     ]:
    #     self.strategy.aggregate_evaluate()

    # aggregate
    def handle_event(self, event):
        receipt = self.w3.eth.waitForTransactionReceipt(event['transactionHash'])
        result = self.contract.events.vvv.processReceipt(receipt)
        print(result[0]['args'])
        rnd = result[0]['args'] # round
        parameters, num_examples = self.get_unaggregated_info() # encoded parameters and num_examples
        results: List[Tuple[Optional[ClientProxy], FitRes]] = to_fit_res_list(parameters, num_examples)
        aggregated_parameters, _ = self.aggregate_fit(rnd, results, None)
        encoded_aggregated_parameters = encode_parameter(aggregated_parameters)
        self.store_aggregated_parameters(encoded_aggregated_parameters)

    def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                self.handle_event(event)
                time.sleep(poll_interval)

    def listen_aggregate_event(self) -> None:

        block_filter = self.w3.eth.filter({'fromBlock':'latest', 'address':self.contract_address})
        self.log_loop(block_filter, 2)

    def get_unaggregated_info(self):
        parameters, num_examples = self.contract.functions.get().call()
        return parameters, num_examples

    def store_aggregated_parameters(self, parameters: str) -> None:

        nonce = self.w3.eth.get_transaction_count(self.contract_address)
        transaction = self.contract.functions.store(
            parameters).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'from': self.account,
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.signTransaction(transaction, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # tx_hash == signed_tx.hash if tx success
        # self.w3.eth.wait_for_transaction_receipt(signed_tx.hash)

# tool.py
def decode_parameter(parameters: str) -> Parameters:
    return Parameters

def encode_parameter(parameters: Parameters) -> str:
    return "Parameters"

def to_fit_res_list(parameters, number_examples) -> List[Tuple[Optional[ClientProxy], FitRes]]:
    results: List[Tuple[Optional[ClientProxy], FitRes]] = []
    for i in len(parameters):
        fitRes: FitRes
        fitRes.num_examples = int(number_examples[i])
        fitRes.parameters = decode_parameter(parameters[i])
        results.append(None, fitRes)
    return results