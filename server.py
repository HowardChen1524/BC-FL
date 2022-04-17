import flwr as fl

if __name__ == "__main__":
    # actor: validator -> 1
    fl.server.start_server(config={"num_rounds": 3, "actor": 1})
