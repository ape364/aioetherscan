from typing import Union, Optional, List, Dict

from aioetherscan.modules.base import BaseModule


class Logs(BaseModule):
    """Event logs

    https://etherscan.io/apis#logs
    """

    _TOPIC_OPERATORS = ('and', 'or')
    _BLOCKS = ('latest',)

    @property
    def _module(self) -> str:
        return 'logs'

    async def get_logs(
            self,
            from_block: Union[int, str],
            to_block: Union[int, str],
            address: str,
            topics: List[str],
            topic_operators: Optional[List[str]] = None
    ) -> List[Dict]:
        """[Beta] The Event Log API was designed to provide an alternative to the native eth_getLogs

        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getlogs.
        """
        return await self._get(
            action='getLogs',
            fromBlock=self._check_block(from_block),
            toBlock=self._check_block(to_block),
            address=address,
            **self._fill_topics(topics, topic_operators)
        )

    def _check_block(self, block: Union[str, int]) -> Union[str, int]:
        if isinstance(block, int):
            return block
        if block in self._BLOCKS:
            return block
        raise ValueError(f'Invalid value {block!r}, only integers or {self._BLOCKS} are supported.')

    def _fill_topics(self, topics: List[str], topic_operators: List[str]):
        if len(topics) > 1:
            self._check_topics(topics, topic_operators)

            topic_params = {
                f'topic{idx}': value
                for idx, value in enumerate(topics)
            }
            topic_operator_params = {
                f'topic{idx}_{idx + 1}_opr': value
                for idx, value in enumerate(topic_operators)
            }

            return {**topic_params, **topic_operator_params}
        else:
            return {'topic0': topics[0]}

    def _check_topics(self, topics: List[str], topic_operators: List[str]) -> None:
        if not topic_operators:
            raise ValueError('Topic operators are required when more than 1 topic passed.')

        for op in topic_operators:
            if op not in self._TOPIC_OPERATORS:
                raise ValueError(f'Invalid topic operator {op!r}, must be one of: {self._TOPIC_OPERATORS}')

        if len(topics) - len(topic_operators) != 1:
            raise ValueError(f'Invalid length of topic_operators list, must be len(topics) - 1.')
