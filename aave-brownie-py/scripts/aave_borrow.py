from scripts.helpful_scripts import get_account
from brownie import config, network, accounts, interface
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow")
    # need to get DAI in terms of ETH
    link_eth_price = get_asset_price(
        config["networks"][network.show_active()]["link_eth_price_feed"]
    )
    amount_link_to_borrow = (1 / link_eth_price) * (borrowable_eth * 0.65)
    print(f"We are going to borrow {amount_link_to_borrow} LINK")
    # now we are going to borrow
    link_address = config["networks"][network.show_active()]["link_token"]
    borrow_tx = lending_pool.borrow(
        link_address,
        Web3.toWei(amount_link_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We Borrowed Some LINK!")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    print(
        "You just deposited, borrowed, and repaid with AAVE, brownie, and chainlink!!"
    )


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["link_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["link_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!!")


def get_asset_price(price_feed_address):
    # need to grab an ABI and an Address, as usual
    link_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = link_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The LINK/ETH price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} of ETH deposited")
    print(f"You have {total_debt_eth} of ETH borrowed")
    print(f"You can borrow {available_borrow_eth} of ETH deposited")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 Token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    # abi
    # address


# left off at 9:24 - going to pull some call data from AAVE about user, which will let us determine how much can be borrowed (LTV)
