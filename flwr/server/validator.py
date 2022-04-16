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

# ---tool.py---
def encode_parameters(results: List[Tuple[FitRes,ClientProxy]]) -> str:
    # encode
    en_result = ""
    num_clients = len(results)
    en_result = en_result + str(num_clients) + '[nclient]'
    for i in range(num_clients):
        clientProxy = results[i][1] 
        num_layers = len(results[i][0])
        en_result = en_result + str(clientProxy) + ',' + str(num_layers) + '[proxy&nlayer]'
        for j in range(num_layers):
            if len(results[0][0][j].shape)==1:
                shape = str(results[0][0][j].shape[0])
            else:
                shape = str(results[0][0][j].shape[0]) + ',' + str(results[0][0][j].shape[1])
            weight_base64_str = base64.b64encode(results[0][0][j]).decode("utf-8")
            layer_info = shape + '[shape]' + weight_base64_str
            if j != num_layers-1:
                en_result = en_result + layer_info + '[layer_info]'
            else:
                en_result = en_result + layer_info
        if i !=  (num_clients-1):
            en_result = en_result + '[client_info]'
    en_result_bytes = en_result.encode('utf-8')    
    en_result_base64_str = base64.b64encode(en_result_bytes).decode("utf-8")

    return en_result_base64_str

def decode_parameter(parameter: str) -> List[Tuple[FitRes,ClientProxy]]:
    # decode
    final_result_list = list()
    de_result = base64.b64decode(parameter.encode("utf-8")).decode("utf-8")
    client_num, de_result = de_result.split("[nclient]")
    client = de_result.split("[client_info]")
    for i in range(int(client_num)):
        weight_result_list = list()
        p, l = client[i].split("[proxy&nlayer]")
        proxy, layer_num = p.split(',')
        all_layer_info = l.split("[layer_info]")
        for j in range(int(layer_num)):
            shape, weight_base64_str = all_layer_info[j].split("[shape]")
            weight = np.frombuffer(base64.decodebytes(weight_base64_str.encode("utf-8")), dtype=np.float32)    
            if "," in shape:
                row, col = shape.split(',')
                shape = (int(row),int(col))
            else:    
                shape = (int(shape),)
            weight = weight.reshape(shape)
            weight_result_list.append(weight)
        final_result_list.append((weight_result_list,int(proxy)))
    return final_result_list
