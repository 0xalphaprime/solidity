from brownie import accounts, config, SimpleStorage, network


def deploy_simple_storage():
    account = get_account()
    # print(account)
    # account = accounts.load("0xmiami")
    # print(account)
    account = accounts.add(config["wallets"]["from_key"])
    simple_storage = SimpleStorage.deploy({"from": account})
    # brownie smart enough to know whether it is a transact or call event
    stored_value = simple_storage.retrieve()
    print(f"The current stored value is:", stored_value)
    transaction = simple_storage.store(4, {"from": account})
    transaction.wait(1)
    updated_stored_value = simple_storage.retrieve()
    print(f"The UPDATED stored value is:", updated_stored_value)


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_simple_storage()
