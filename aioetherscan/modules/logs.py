from typing import Optional, Literal

from aioetherscan.modules.base import BaseModule

TopicNumber = Literal[0, 1, 2, 3]
TopicOperator = Literal['and', 'or']


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
        topics: Optional[dict[TopicNumber, str]] = None,
        topic_operators: Optional[list[tuple[TopicNumber, TopicNumber, TopicOperator]]] = None,
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
            **self._fill_topics(topics, topic_operators),
        )

    def _fill_topics(
        self, topics: Optional[dict[int, str]], topic_operators: Optional[list[str]]
    ) -> dict[str, str]:
        if not topics:
            return {}

        if len(topics) == 1:
            topic_number, topic = topics.popitem()
            return {f'topic{topic_number}': topic}

        if not topic_operators:
            raise ValueError('Topic operators are required when more than 1 topic passed.')

        return {
            **{f'topic{topic_number}': topic for topic_number, topic in topics.items()},
            **{
                self._get_topic_operator(first, second): opr
                for first, second, opr in topic_operators
            },
        }

    @staticmethod
    def _get_topic_operator(topic_one: TopicNumber, topic_two: TopicNumber) -> str:
        if topic_one == topic_two:
            raise ValueError('Topic numbers must be different when using topic operators.')
        return f'topic{topic_one}_{topic_two}_opr'
