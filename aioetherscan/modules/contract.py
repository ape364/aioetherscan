from typing import Dict, List

from aioetherscan.modules.base import BaseModule


class Contract(BaseModule):
    """Contract APIs

    https://etherscan.io/apis#contracts
    """

    @property
    def _module(self) -> str:
        return 'contract'

    async def contract_abi(self, address: str) -> str:
        """Get Contract ABI for Verified Contract Source Codes

        https://etherscan.io/contractsVerified.
        """
        return await self._get(
            action='getabi',
            address=address
        )

    async def contract_source_code(self, address: str) -> List[Dict]:
        """Get Contract Source Code for Verified Contract Source Codes

        https://etherscan.io/contractsVerified.
        """
        return await self._get(
            action='getsourcecode',
            address=address
        )

    async def verify_contract_source_code(
            self,
            contract_address: str,
            source_code: str,
            contract_name: str,
            compiler_version: str,
            optimization_used: bool = False,
            runs: int = 200,
            constructor_arguements: str = None,
            libraries: Dict[str, str] = None
    ) -> str:
        """[BETA] Verify Source Code"""
        return await self._post(
            module='contract',
            action='verifysourcecode',
            contractaddress=contract_address,
            sourceCode=source_code,
            contractname=contract_name,
            compilerversion=compiler_version,
            optimizationUsed=1 if optimization_used else 0,
            runs=runs,
            constructorArguements=constructor_arguements,
            **self._parse_libraries(libraries or {})
        )

    async def check_verification_status(self, guid: str) -> str:
        """Check Source code verification submission status"""
        return await self._get(
            action='checkverifystatus',
            guid=guid
        )

    @staticmethod
    def _parse_libraries(libraries: Dict[str, str]) -> Dict[str, str]:
        return dict(
            part
            for i, (name, address) in enumerate(libraries.items(), start=1)
            for part in (
                (f'libraryname{i}', name),
                (f'libraryaddress{i}', address)
            )
        )
