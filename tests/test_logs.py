from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def logs():
    c = Client('TestApiKey')
    yield c.logs
    await c.close()


def test_module(logs):
    assert logs._module == 'logs'


@pytest.mark.asyncio
async def test_get_logs_raises_value_error_when_no_address_or_topics_provided(logs):
    with pytest.raises(ValueError):
        await logs.get_logs()


@pytest.mark.asyncio
async def test_get_logs_calls_get_with_correct_parameters(logs):
    logs._get = AsyncMock(return_value=[])
    await logs.get_logs(address='0x123', from_block=1, to_block=2)
    logs._get.assert_called_once_with(
        action='getLogs',
        address='0x123',
        fromBlock=1,
        toBlock=2,
        page=None,
        offset=None,
    )


@pytest.mark.asyncio
async def test_get_logs_calls_fill_topics_with_correct_parameters(logs):
    logs._get = AsyncMock(return_value=[])
    logs._fill_topics = Mock(return_value={})
    await logs.get_logs(topics={0: '0x123'}, operators=[(0, 1, 'and')])
    logs._fill_topics.assert_called_once_with(
        {0: '0x123'},
        [(0, 1, 'and')],
    )


@pytest.mark.asyncio
async def test_get_logs_returns_result_of_get(logs):
    logs._get = AsyncMock(return_value=[{'log': 'entry'}])
    result = await logs.get_logs(address='0x123', from_block=1, to_block=2)
    assert result == [{'log': 'entry'}]


@pytest.mark.asyncio
async def test_get_logs_calls_get_with_page_and_offset(logs):
    logs._get = AsyncMock(return_value=[])
    await logs.get_logs(address='0x123', from_block=1, to_block=2, page=3, offset=10)
    logs._get.assert_called_once_with(
        action='getLogs',
        address='0x123',
        fromBlock=1,
        toBlock=2,
        page=3,
        offset=10,
    )


@pytest.mark.asyncio
async def test_get_logs_raises_value_error_when_both_address_and_topics_are_empty(logs):
    with pytest.raises(ValueError):
        await logs.get_logs()


def test_fill_topics_none(logs):
    topics = None
    topic_operators = None
    assert logs._fill_topics(topics, topic_operators) == {}


def test_fill_topics_one_element(logs):
    topics = {0: '0x123'}
    topic_operators = None
    assert logs._fill_topics(topics, topic_operators) == {'topic0': '0x123'}


def test_fill_topics_multiple_elements_none(logs):
    topics = {0: '0x123', 1: '0x456'}
    topic_operators = None
    with pytest.raises(ValueError):
        logs._fill_topics(topics, topic_operators)


def test_fill_topics_multiple_elements_operators(logs):
    topics = {0: '0x123', 1: '0x456', 3: '0x789'}
    topic_operators = {(0, 1, 'and'), (1, 2, 'or'), (0, 3, 'or')}
    assert logs._fill_topics(topics, topic_operators) == {
        'topic0': '0x123',
        'topic1': '0x456',
        'topic3': '0x789',
        'topic0_1_opr': 'and',
        'topic1_2_opr': 'or',
        'topic0_3_opr': 'or',
    }


def test_fill_topic_operators_ok(logs):
    topic_operators = {(0, 1, 'and'), (1, 2, 'or'), (0, 3, 'or'), (0, 2, 'and')}
    assert logs._fill_topic_operators(topic_operators) == {
        'topic0_1_opr': 'and',
        'topic1_2_opr': 'or',
        'topic0_3_opr': 'or',
        'topic0_2_opr': 'and',
    }


@pytest.mark.parametrize(
    'topic_operators',
    [
        {(0, 1, 'and'), (1, 0, 'or'), (0, 3, 'or')},  # duplicate
        {(0, 1, 'and'), (1, 2, 'or'), (3, 3, 'or')},  # same topic twice
        {(0, 1, 'and'), (1, 0, 'or'), (3, 3, 'or')},  # both
    ],
)
def test_fill_topic_operators_exception(logs, topic_operators):
    with pytest.raises(ValueError) as exc_info:
        logs._fill_topic_operators(topic_operators)
    assert (
        str(exc_info.value)
        == 'Topic operators must be used with 2 different topics without duplicates.'
    )
