from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def contract():
    c = Client('TestApiKey')
    yield c.contract
    await c.close()


@pytest.mark.asyncio
async def test_contract_abi(contract):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await contract.contract_abi('0x012345')
        mock.assert_called_once_with(params=dict(module='contract', action='getabi', address='0x012345'))


@pytest.mark.asyncio
async def test_contract_source_code(contract):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await contract.contract_source_code('0x012345')
        mock.assert_called_once_with(params=dict(module='contract', action='getsourcecode', address='0x012345'))


@pytest.mark.asyncio
async def test_verify_contract_source_code(contract):
    with patch('aioetherscan.network.Network.post', new=CoroutineMock()) as mock:
        await contract.verify_contract_source_code(
            contract_address='0x012345',
            source_code='some source code\ntest',
            contract_name='some contract name',
            compiler_version='1.0.0',
            optimization_used=False,
            runs=123,
            constructor_arguements='some args'
        )
        mock.assert_called_once_with(
            data=dict(
                module='contract',
                action='verifysourcecode',
                contractaddress='0x012345',
                sourceCode='some source code\ntest',
                contractname='some contract name',
                compilerversion='1.0.0',
                optimizationUsed=0,
                runs=123,
                constructorArguements='some args'
            )
        )

    with patch('aioetherscan.network.Network.post', new=CoroutineMock()) as mock:
        await contract.verify_contract_source_code(
            contract_address='0x012345',
            source_code='some source code\ntest',
            contract_name='some contract name',
            compiler_version='1.0.0',
            optimization_used=False,
            runs=123,
            constructor_arguements='some args',
            libraries={'one_name': 'one_addr', 'two_name': 'two_addr'}
        )
        mock.assert_called_once_with(
            data=dict(
                module='contract',
                action='verifysourcecode',
                contractaddress='0x012345',
                sourceCode='some source code\ntest',
                contractname='some contract name',
                compilerversion='1.0.0',
                optimizationUsed=0,
                runs=123,
                constructorArguements='some args',
                libraryname1='one_name',
                libraryaddress1='one_addr',
                libraryname2='two_name',
                libraryaddress2='two_addr',
            )
        )


@pytest.mark.asyncio
async def test_check_verification_status(contract):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await contract.check_verification_status('some_guid')
        mock.assert_called_once_with(params=dict(module='contract', action='checkverifystatus', guid='some_guid'))


def test_parse_libraries(contract):
    mydict = {
        'lib1': 'addr1',
        'lib2': 'addr2',
    }
    expected = {
        'libraryname1': 'lib1',
        'libraryaddress1': 'addr1',
        'libraryname2': 'lib2',
        'libraryaddress2': 'addr2'
    }
    assert contract._parse_libraries(mydict) == expected

    mydict = {
        'lib1': 'addr1',
    }
    expected = {
        'libraryname1': 'lib1',
        'libraryaddress1': 'addr1',
    }
    assert contract._parse_libraries(mydict) == expected

    mydict = {}
    expected = {}
    assert contract._parse_libraries(mydict) == expected
