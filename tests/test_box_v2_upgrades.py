from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    config,
    network
)
import pytest


def test_box_v2_upgrades():
    account = get_account()
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False),
    )
    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False),
    )
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False),
    )
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    assert proxy_box.retrieve() == 0

    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1

    # Upgrade contract Box to BoxV2
    # with pytest.raises(exceptions.VirtualMachineError):
    #    proxy_box.increment({"from": account})

    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False),
    )
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin)
    upgrade_transaction.wait(1)

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 2
