import subprocess
from pathlib import Path
import shutil
import json
from pathlib import Path
BC_ACCOUNTS_PATH: str = f"{Path(__file__).parent.absolute()}/accounts"
BC_BOOTNODE_KEY_PATH: str = f"{Path(__file__).parent.absolute()}/config/boot.key"
BC_PASSWORD_PATH: str = f"{Path(__file__).parent.absolute()}/config/password.txt"
BC_GENESIS_PATH: str = f"{Path(__file__).parent.absolute()}/config/genesis.json"

# from flwr.blockchain import BC_ACCOUNTS_PATH, BC_BOOTNODE_KEY_PATH, BC_PASSWORD_PATH, BC_GENESIS_PATH

def run_cmd(cmd=None):
    if cmd:
        success = True
        out = None
        p = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        if p.poll() == 0:
            out, err = p.communicate()
        else:
            success = False
        return success, out

def create_account(actor, id):
    success = False
    data_dir = f"{BC_ACCOUNTS_PATH}/{actor}{id}/data"
    if(Path(data_dir).exists()):
        return False
    cmd = f'geth --datadir {data_dir} account new --password {BC_PASSWORD_PATH}'
    n_success, n_out = run_cmd(cmd)
    print("%s%d create account: %r" % (actor, id, n_success))
    if n_success:
        print("accounts created in:",data_dir)
        cmd = f'geth --datadir {data_dir} init {BC_GENESIS_PATH}'
        i_success, i_out = run_cmd(cmd)
        print("%s%d init genesis: %r" % (actor, id, i_success))
        if i_success:
            success = True
    return success

def revert():
    print("remove folder:",BC_ACCOUNTS_PATH)
    shutil.rmtree(BC_ACCOUNTS_PATH)

def has_false(arr):
    return not all(all(i) for i in arr)

# create accounts
def create_accounts(actors, amounts):
    assert len(actors) == len(amounts) and len(actors) > 0
    return [[create_account(actors[i], j) for j in range(amounts[i])] for i in range(len(actors))]

def export(actors, amounts):
    assert len(actors) == len(amounts) and len(actors) > 0
    info = {}
    for i in range(len(actors)):
        account_arr = []
        for j in range(amounts[i]):
            actor_name = "%s%d" % (actors[i], j)
            data_dir = f"{BC_ACCOUNTS_PATH}/{actor_name}/data/keystore"
            first_file = next(Path(data_dir).iterdir())
            f = open(first_file, "r")
            json_obj = json.loads(f.read())
            account = json_obj['address']
            account_arr.append(account)
            info[actors[i]] = account_arr

    out_folder = f"{BC_ACCOUNTS_PATH}/accounts.json"
    with open(out_folder, 'w') as outfile:
        outfile.write(json.dumps(info, ensure_ascii=False, indent=4))
    return info

def create_accounts_V2(actors, amounts):
    result = create_accounts(actors, amounts)
    # print(result)
    # remove if the folder already exists
    return export(actors, amounts)
    # if has_false(result):
    #     revert()

def clean_accounts():
    revert()
# create accounts
# if __name__ == "__main__":
#     # actors = ['aggregator', 'validator', 'trainer']
#     # amounts = [1, 0, 0]
#     actors = ['aggregator']
#     amounts = [1]
#     # create_accounts(actors, amounts)
#     create_accounts_V2(actors, amounts)
#     # clean_accounts()