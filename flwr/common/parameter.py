# Copyright 2020 Adap GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Parameter conversion."""


from io import BytesIO
from typing import cast, List, Tuple, Optional
from flwr.server.client_proxy import ClientProxy
import base64

import numpy as np

from .typing import Parameters, Weights, FitRes

def weights_to_parameters(weights: Weights) -> Parameters:
    """Convert NumPy weights to parameters object."""
    tensors = [ndarray_to_bytes(ndarray) for ndarray in weights]
    return Parameters(tensors=tensors, tensor_type="numpy.nda")


def parameters_to_weights(parameters: Parameters) -> Weights:
    """Convert parameters object to NumPy weights."""
    return [bytes_to_ndarray(tensor) for tensor in parameters.tensors]


def ndarray_to_bytes(ndarray: np.ndarray) -> bytes:
    """Serialize NumPy array to bytes."""
    bytes_io = BytesIO()
    np.save(bytes_io, ndarray, allow_pickle=False)
    return bytes_io.getvalue()


def bytes_to_ndarray(tensor: bytes) -> np.ndarray:
    """Deserialize NumPy array from bytes."""
    bytes_io = BytesIO(tensor)
    ndarray_deserialized = np.load(bytes_io, allow_pickle=False)
    return cast(np.ndarray, ndarray_deserialized)

def encode_weights(results: List[Tuple[Weights, int]]) -> str:
    """Encode Client Results to str."""
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

def decode_weights(parameter: str) -> List[Tuple[Weights, int]]:
    """Decode str to Client Results."""
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

def parametersList_to_fitResList(client_parameters_list: List[Tuple[Parameters, int]]) -> List[Tuple[Optional[ClientProxy], FitRes]]:
    results: List[Tuple[Optional[ClientProxy], FitRes]] = []
    for client_parameters in client_parameters_list:
        fitRes = FitRes(parameters=client_parameters[0], num_examples=client_parameters[1])
        results.append((None, fitRes))
    return results