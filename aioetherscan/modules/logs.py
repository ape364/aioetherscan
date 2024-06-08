from typing import Optional, Literal

from aioetherscan.modules.base import BaseModule

TopicNumber = Literal[0, 1, 2, 3]
TopicOperator = Literal['and', 'or']

Topics = dict[TopicNumber, str]
TopicOperators = set[tuple[TopicNumber, TopicNumber, TopicOperator]]


class Logs(BaseModule):
    """Logs

    https://docs.etherscan.io/api-endpoints/logs
    """

    @property
    def _module(self) -> str:
        return 'logs'

    async def get_logs(
        self,
        address: Optional[str] = None,
        topics: Optional[Topics] = None,
        operators: Optional[TopicOperators] = None,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
        page: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[dict]:
        """Get Event Logs by address and/or topics"""

        if address is None and topics is None:
            raise ValueError('Either address or topics must be passed.')

        return await self._get(
            action='getLogs',
            fromBlock=from_block,
            toBlock=to_block,
            address=address,
            page=page,
            offset=offset,
            **self._fill_topics(topics, operators),
        )

    def _fill_topics(
        self, topics: Optional[Topics], operators: Optional[TopicOperators]
    ) -> dict[str, str]:
        if not topics:
            return {}

        if len(topics) == 1:
            topic_number, topic = topics.popitem()
            return {f'topic{topic_number}': topic}

        if not operators:
            raise ValueError('Topic operators are required when more than 1 topic passed.')

        return {
            **{f'topic{topic_number}': topic for topic_number, topic in topics.items()},
            **self._fill_topic_operators(operators),
        }

    @staticmethod
    def _fill_topic_operators(operators: TopicOperators) -> dict[str, str]:
        same_topic_twice = 1 in (len(set(i[:2])) for i in operators)
        duplicate = len({frozenset(sorted(i[:2])) for i in operators}) != len(operators)

        if same_topic_twice or duplicate:
            raise ValueError(
                'Topic operators must be used with 2 different topics without duplicates.'
            )

        return {f'topic{first}_{second}_opr': opr for first, second, opr in operators}
