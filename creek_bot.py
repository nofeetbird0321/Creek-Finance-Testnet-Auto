#!/usr/bin/env python3
"""
Creek Finance Automation Bot - Python Version
Auto Bot for Creek Finance on SUI Testnet using pysui

This script automates DeFi activities on SUI Testnet including:
- Token faucet claims (XAUM, USDC)
- Token swaps (USDC ↔ GUSD)
- Staking and redeeming XAUM
- Lending protocol operations (deposit, borrow, repay, withdraw)
- Health factor monitoring

SECURITY WARNING: This bot handles private keys. Ensure proper security measures.
"""

import asyncio
import time
import random
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from pathlib import Path

from pysui import SuiConfig, SyncClient
from pysui.sui.sui_types.scalars import ObjectID, SuiString
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_crypto import keypair_from_keystring
import requests


# ============================================
# CONFIGURATION
# ============================================
class Config:
    """Bot configuration constants"""
    
    # Network Configuration
    RPC_URL = 'https://sui-testnet-rpc.publicnode.com'
    NETWORK = 'testnet'
    
    # File Paths
    PRIVATE_KEYS_FILE = 'privatekey.txt'
    PROXY_FILE = 'proxy.txt'
    
    # Faucet Configuration
    SUI_FAUCET_URL = 'https://faucet.testnet.sui.io/v2/gas'
    SUI_FAUCET_RETRIES = 50
    MIN_SUI_BALANCE = 1.0
    
    # Constants
    MIST_PER_SUI = 1_000_000_000
    DECIMALS = 1_000_000_000
    GAS_BUDGET = 200_000_000
    
    # Operation Counts
    XAUM_CLAIM_COUNT = 3
    USDC_CLAIM_COUNT = 3
    SWAP_USDC_TO_GUSD_COUNT = 3
    SWAP_GUSD_TO_USDC_COUNT = 1
    STAKE_XAUM_COUNT = 3
    REDEEM_XAUM_COUNT = 3
    DEPOSIT_GR_COUNT = 3
    DEPOSIT_SUI_COUNT = 3
    DEPOSIT_USDC_COUNT = 3
    BORROW_GUSD_COUNT = 3
    REPAY_GUSD_COUNT = 3
    WITHDRAW_COUNT = 3
    
    # Retry Configuration
    COIN_FETCH_RETRIES = 5
    RATE_LIMIT_COOLDOWN = 30
    
    # Contract Addresses
    FAUCET_PACKAGE = '0xa03cb0b29e92c6fa9bfb7b9c57ffdba5e23810f20885b4390f724553d32efb8b'
    XAUM_SHARED_OBJECT = '0x66984752afbd878aaee450c70142747bb31fca2bb63f0a083d75c361da39adb1'
    USDC_SHARED_OBJECT = '0x77153159c4e3933658293a46187c30ef68a8f98aa48b0ce76ffb0e6d20c0776b'
    
    GUSD_PACKAGE = '0x8cee41afab63e559bc236338bfd7c6b2af07c9f28f285fc8246666a7ce9ae97a'
    GUSD_VAULT = '0x1fc1b07f7c1d06d4d8f0b1d0a2977418ad71df0d531c476273a2143dfeffba0e'
    GUSD_MARKET = '0x166dd68901d2cb47b55c7cfbb7182316f84114f9e12da9251fd4c4f338e37f5d'
    
    STAKING_MANAGER = '0x5c9d26e8310f740353eac0e67c351f71bad8748cf5ac90305ffd32a5f3326990'
    CLOCK_OBJECT = '0x0000000000000000000000000000000000000000000000000000000000000006'
    
    LENDING_PACKAGE = '0x8cee41afab63e559bc236338bfd7c6b2af07c9f28f285fc8246666a7ce9ae97a'
    PROTOCOL_OBJECT = '0x13f4679d0ebd6fc721875af14ee380f45cde02f81d690809ac543901d66f6758'
    LENDING_MARKET = '0x166dd68901d2cb47b55c7cfbb7182316f84114f9e12da9251fd4c4f338e37f5d'
    XORACLE_OBJECT = '0x9052b77605c1e2796582e996e0ce60e2780c9a440d8878a319fa37c50ca32530'
    PRICE_ORACLE = '0x3a865c5bc0e47efc505781598396d75b647e4f1218359e89b08682519c3ac060'
    ORACLE_PACKAGE = '0xca9b2f66c5ab734939e048d0732e2a09f486402bb009d88f95c27abe8a4872ee'
    RULE_PACKAGE = '0xbd6d8bb7f40ca9921d0c61404cba6dcfa132f184cf8c0f273008a103889eb0e8'
    
    # Token Types
    USDC_TYPE = '0xa03cb0b29e92c6fa9bfb7b9c57ffdba5e23810f20885b4390f724553d32efb8b::usdc::USDC'
    GUSD_TYPE = '0x5434351f2dcae30c0c4b97420475c5edc966b02fd7d0bbe19ea2220d2f623586::coin_gusd::COIN_GUSD'
    XAUM_TYPE = '0xa03cb0b29e92c6fa9bfb7b9c57ffdba5e23810f20885b4390f724553d32efb8b::coin_xaum::COIN_XAUM'
    GY_TYPE = '0x0ac2d5ebd2834c0db725eedcc562c60fa8e281b1772493a4d199fd1e70065671::coin_gy::COIN_GY'
    GR_TYPE = '0x5504354cf3dcbaf64201989bc734e97c1d89bba5c7f01ff2704c43192cc2717c::coin_gr::COIN_GR'
    SUI_TYPE = '0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI'


class HealthFactorConfig:
    """Health factor calculation configuration"""
    
    DEPOSIT_PERCENTAGE = {
        'GR': 0.70,
        'SUI': 0.50,
        'USDC': 0.80
    }
    
    MIN_RESERVE = {
        'GR': 50 * 1e9,
        'SUI': 1 * 1e9,
        'USDC': 5 * 1e9
    }
    
    # WARNING: These are hardcoded prices - should be fetched from oracles
    PRICE = {
        'GR': 150.5,
        'SUI': 3.18,
        'USDC': 1.0,
        'GUSD': 1.05
    }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_random_delay(min_sec: int, max_sec: int) -> int:
    """Get random delay in seconds"""
    return random.randint(min_sec, max_sec)


async def delay(seconds: int, message: str = 'Waiting'):
    """Async delay with logging"""
    print(f"⏳ {message} {seconds}s...")
    await asyncio.sleep(seconds)


def get_random_amount(min_val: float, max_val: float, decimals: int = Config.DECIMALS) -> int:
    """Get random amount with decimals"""
    return int((random.uniform(min_val, max_val)) * decimals)


def read_private_keys(filename: str = Config.PRIVATE_KEYS_FILE) -> List[str]:
    """Read private keys from file
    
    Security: This reads plain text keys. In production, use encrypted storage.
    """
    filepath = Path(filename)
    if not filepath.exists():
        print(f"❌ File {filename} not found!")
        return []
    
    try:
        with open(filepath, 'r') as f:
            keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return keys
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return []


def read_proxy_mappings(filename: str = Config.PROXY_FILE) -> Dict[str, Optional[str]]:
    """Read proxy mappings from file"""
    filepath = Path(filename)
    if not filepath.exists():
        print(f"⚠️ File {filename} not found - using local IP for all wallets\n")
        return {}
    
    try:
        proxies = {}
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for index, line in enumerate(lines, 1):
                trimmed = line.strip()
                if trimmed and not trimmed.startswith('#'):
                    proxies[f'pk{index}'] = trimmed
                else:
                    proxies[f'pk{index}'] = None
        return proxies
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return {}


def get_proxy_for_wallet(wallet_index: int, proxy_mappings: Dict) -> Optional[str]:
    """Get proxy URL for specific wallet"""
    key = f'pk{wallet_index}'
    proxy = proxy_mappings.get(key)
    
    if not proxy:
        print(f"  🌍 Local IP")
        return None
    
    print(f"  🔗 Proxy: {proxy}")
    return proxy


class WalletManager:
    """Manages wallet operations"""
    
    def __init__(self, client: SyncClient):
        self.client = client
    
    def import_wallet(self, private_key: str) -> Optional[Tuple[any, str]]:
        """Import wallet from private key string
        
        Args:
            private_key: Private key string (suiprivkey format)
            
        Returns:
            Tuple of (keypair, address) or None if failed
        """
        try:
            # Import keypair from keystring
            keypair = keypair_from_keystring(private_key)
            address = keypair.to_address()
            return (keypair, address)
        except Exception as e:
            print(f"Error importing wallet: {str(e)}")
            return None
    
    def get_sui_balance(self, address: str) -> float:
        """Get SUI balance for address"""
        try:
            result = self.client.get_gas(address)
            if result.is_ok():
                total = sum(int(coin.balance) for coin in result.result_data.data)
                return total / Config.MIST_PER_SUI
            return 0.0
        except Exception as e:
            print(f"Error getting SUI balance: {str(e)}")
            return 0.0
    
    def get_coins(self, address: str, coin_type: str) -> List:
        """Get coins of specific type for address"""
        try:
            result = self.client.get_coin(address, coin_type)
            if result.is_ok():
                return result.result_data.data
            return []
        except Exception as e:
            # Handle rate limiting
            if '429' in str(e):
                print(f"  ⚠️ Rate limited! Waiting {Config.RATE_LIMIT_COOLDOWN}s...")
                time.sleep(Config.RATE_LIMIT_COOLDOWN)
                try:
                    result = self.client.get_coin(address, coin_type)
                    if result.is_ok():
                        return result.result_data.data
                except Exception as retry_error:
                    print(f"  ✗ Still failed: {str(retry_error)}")
            return []
    
    def get_token_balance(self, address: str, token_type: str) -> float:
        """Get balance for specific token type"""
        try:
            if token_type == Config.SUI_TYPE:
                return self.get_sui_balance(address)
            else:
                coins = self.get_coins(address, token_type)
                total = sum(int(coin.balance) for coin in coins)
                return total / Config.DECIMALS
        except Exception as e:
            print(f"Error getting token balance: {str(e)}")
            return 0.0


class FaucetManager:
    """Manages faucet operations"""
    
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
    
    def request_sui_faucet(self, address: str, proxy: Optional[str] = None) -> Dict:
        """Request SUI from testnet faucet"""
        try:
            payload = {
                'FixedAmountRequest': {
                    'recipient': address
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            response = requests.post(
                Config.SUI_FAUCET_URL,
                json=payload,
                headers=headers,
                proxies=proxies,
                timeout=30
            )
            
            if response.status_code == 429:
                return {'success': False, 'error': 'Rate limit', 'isRateLimit': True}
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'status' in data and 'Failure' in data['status']:
                        error = data['status']['Failure'].get('Internal', 'Error')
                        return {'success': False, 'error': error}
                    return {'success': True, 'data': data}
                except Exception as e:
                    return {'success': False, 'error': 'Invalid JSON'}
            
            return {'success': False, 'error': f'Status {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def ensure_sui_faucet(self, address: str, proxy: Optional[str] = None) -> bool:
        """Ensure wallet has minimum SUI balance"""
        print(f"\n💧 Ensuring wallet has minimum {Config.MIN_SUI_BALANCE} SUI...")
        
        for attempt in range(1, Config.SUI_FAUCET_RETRIES + 1):
            current_balance = self.wallet_manager.get_sui_balance(address)
            print(f"  📊 Balance: {current_balance:.6f} SUI ({attempt}/{Config.SUI_FAUCET_RETRIES})")
            
            if current_balance >= Config.MIN_SUI_BALANCE:
                print(f"  ✓ Balance sufficient!")
                return True
            
            print(f"  💧 Requesting SUI Faucet...")
            result = self.request_sui_faucet(address, proxy)
            
            if result['success']:
                print(f"  ✓ Faucet success!")
                await delay(3, 'Balance update:')
            else:
                print(f"  ✗ Failed: {result['error']}")
                if result.get('isRateLimit'):
                    await delay(get_random_delay(3, 10), 'Rate limit:')
                elif attempt < Config.SUI_FAUCET_RETRIES:
                    await delay(get_random_delay(3, 10), 'Retry:')
        
        final_balance = self.wallet_manager.get_sui_balance(address)
        if final_balance >= Config.MIN_SUI_BALANCE:
            print(f"  ✓ Balance sufficient!")
            return True
        
        print(f"  ✗ Failed after {Config.SUI_FAUCET_RETRIES} attempts")
        return False


def calculate_safe_deposit_amount(current_balance: float, token_type: str) -> int:
    """Calculate safe deposit amount based on health factor"""
    deposit_pct = HealthFactorConfig.DEPOSIT_PERCENTAGE.get(token_type, 0.7)
    min_reserve = HealthFactorConfig.MIN_RESERVE.get(token_type, 0)
    
    deposit_by_pct = current_balance * deposit_pct
    deposit_with_reserve = current_balance - min_reserve
    
    safe_deposit = min(deposit_by_pct, deposit_with_reserve)
    return max(0, int(safe_deposit))


def calculate_health_factor(address: str, wallet_manager: WalletManager) -> float:
    """Calculate real-time health factor"""
    try:
        gr_balance = wallet_manager.get_token_balance(address, Config.GR_TYPE)
        usdc_balance = wallet_manager.get_token_balance(address, Config.USDC_TYPE)
        gusd_balance = wallet_manager.get_token_balance(address, Config.GUSD_TYPE)
        
        gr_value = gr_balance * HealthFactorConfig.PRICE['GR']
        usdc_value = usdc_balance * HealthFactorConfig.PRICE['USDC']
        total_collateral = gr_value + usdc_value
        
        borrow_value = gusd_balance * HealthFactorConfig.PRICE['GUSD']
        
        health_factor = total_collateral / borrow_value if borrow_value > 0 else float('inf')
        
        status = '✅ VERY SAFE'
        if health_factor < 1.5:
            status = '🚨 CRITICAL!'
        elif health_factor < 2.0:
            status = '⚠️ WARNING'
        elif health_factor < 10:
            status = '✅ SAFE'
        
        print(f"\n📊 ═══════════════════════════════════════════════")
        print(f"   REAL-TIME HEALTH FACTOR SNAPSHOT")
        print(f"   ═══════════════════════════════════════════════")
        print(f"   Collateral: GR {gr_balance:.2f} (${gr_value:.2f}) + USDC {usdc_balance:.2f} (${usdc_value:.2f})")
        print(f"   Total Collateral: ${total_collateral:.2f}")
        print(f"   Borrow: GUSD {gusd_balance:.2f} (${borrow_value:.2f})")
        print(f"   ───────────────────────────────────────────────")
        print(f"   Health Factor: {'∞' if health_factor == float('inf') else f'{health_factor:.2f}'} {status}")
        print(f"   ═══════════════════════════════════════════════\n")
        
        return health_factor
    except Exception as e:
        print(f"Error calculating health factor: {str(e)}")
        return float('inf')


def print_balance_report(address: str, balance_before: Dict, balance_after: Dict):
    """Print balance comparison report"""
    if not balance_before or not balance_after:
        return
    
    print(f"\n{'═' * 70}")
    print(f"  💰 BALANCE TRACKING REPORT")
    print(f"{'═' * 70}")
    print(f"  Address: {address[:12]}...{address[-8:]}")
    print(f"{'─' * 70}")
    print(f"  Token │      Before      │       After      │     Change")
    print(f"{'─' * 70}")
    
    for token in ['GR', 'SUI', 'USDC', 'GUSD', 'XAUM']:
        before = balance_before.get(token, 0)
        after = balance_after.get(token, 0)
        change = after - before
        print(f"  {token:5} │ {before:15.6f} │ {after:15.6f} │ {change:12.6f}")
    
    print(f"{'═' * 70}\n")


# ============================================
# TRANSACTION OPERATIONS
# ============================================

class CreekFinanceBot:
    """Main bot class for Creek Finance operations"""
    
    def __init__(self):
        # Initialize SUI client
        config = SuiConfig.testnet_config()
        config.rpc_url = Config.RPC_URL
        self.client = SyncClient(config)
        
        self.wallet_manager = WalletManager(self.client)
        self.faucet_manager = FaucetManager(self.wallet_manager)
    
    async def claim_xaum_faucet(self, keypair, address: str, attempt_num: int) -> bool:
        """Claim XAUM from faucet"""
        try:
            print(f"  💰 Claim XAUM #{attempt_num}...")
            
            txn = SyncTransaction(client=self.client, initial_sender=SuiAddress(address))
            
            # Build transaction
            txn.move_call(
                target=f"{Config.FAUCET_PACKAGE}::coin_xaum::mint",
                arguments=[
                    ObjectID(Config.XAUM_SHARED_OBJECT),
                    SuiString('1000000000'),
                    SuiAddress(address)
                ]
            )
            
            # Execute transaction
            result = txn.execute(gas_budget=str(Config.GAS_BUDGET))
            
            if result.is_ok():
                print(f"  ✓ Success! TX: {result.result_data.digest[:10]}...")
                await delay(get_random_delay(10, 15), 'Next:')
                return True
            else:
                print(f"  ✗ Failed: {result.result_string}")
                return False
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
    
    async def claim_usdc_faucet(self, keypair, address: str, attempt_num: int) -> bool:
        """Claim USDC from faucet"""
        try:
            print(f"  💵 Claim USDC #{attempt_num}...")
            
            txn = SyncTransaction(client=self.client, initial_sender=SuiAddress(address))
            
            # Build transaction
            txn.move_call(
                target=f"{Config.FAUCET_PACKAGE}::usdc::mint",
                arguments=[
                    ObjectID(Config.USDC_SHARED_OBJECT),
                    SuiString('10000000000'),
                    SuiAddress(address)
                ]
            )
            
            # Execute transaction
            result = txn.execute(gas_budget=str(Config.GAS_BUDGET))
            
            if result.is_ok():
                print(f"  ✓ Success! TX: {result.result_data.digest[:10]}...")
                await delay(get_random_delay(10, 15), 'Next:')
                return True
            else:
                print(f"  ✗ Failed: {result.result_string}")
                return False
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
    
    async def process_wallet(self, keypair, address: str, wallet_index: int, 
                           total_wallets: int, proxy_url: Optional[str] = None) -> Dict:
        """Process all operations for a single wallet
        
        NOTE: This is a simplified version. Full implementation would include:
        - Swap operations (USDC ↔ GUSD)
        - Staking/unstaking XAUM
        - Lending protocol (deposit, borrow, repay, withdraw)
        - Complete error handling and retry logic
        """
        print(f"\n╔{'═' * 48}╗")
        print(f"║  WALLET {wallet_index}/{total_wallets}")
        print(f"╚{'═' * 48}╝")
        print(f"Address: {address}")
        if proxy_url:
            print(f"Proxy: {proxy_url}")
        else:
            print(f"Proxy: 🌍 Local IP")
        print()
        
        # Get initial balance
        balance_before = {
            'GR': self.wallet_manager.get_token_balance(address, Config.GR_TYPE),
            'SUI': self.wallet_manager.get_token_balance(address, Config.SUI_TYPE),
            'USDC': self.wallet_manager.get_token_balance(address, Config.USDC_TYPE),
            'GUSD': self.wallet_manager.get_token_balance(address, Config.GUSD_TYPE),
            'XAUM': self.wallet_manager.get_token_balance(address, Config.XAUM_TYPE),
        }
        
        print(f"\n✅ Initial Balance Snapshot:")
        print(f"   GR: {balance_before['GR']:.2f}, SUI: {balance_before['SUI']:.6f}, "
              f"USDC: {balance_before['USDC']:.2f}, GUSD: {balance_before['GUSD']:.2f}")
        
        stats = {
            'xaumClaims': 0,
            'usdcClaims': 0,
            'success': False
        }
        
        try:
            # Step 1: Ensure SUI balance
            print('━' * 48)
            print('📍 STEP 1: Check & Get SUI Balance')
            print('━' * 48)
            
            if not await self.faucet_manager.ensure_sui_faucet(address, proxy_url):
                print('❌ Failed to get SUI\n')
                return {
                    'success': False,
                    'stats': stats,
                    'balanceBefore': balance_before,
                    'balanceAfter': None
                }
            
            # Step 2: Claim XAUM
            print('\n━' * 48)
            print('📍 STEP 2: Claim XAUM')
            print('━' * 48)
            
            for i in range(1, Config.XAUM_CLAIM_COUNT + 1):
                if await self.claim_xaum_faucet(keypair, address, i):
                    stats['xaumClaims'] += 1
            
            print(f"\n📊 XAUM Claims: {stats['xaumClaims']}/{Config.XAUM_CLAIM_COUNT}")
            
            # Step 3: Claim USDC
            print('\n━' * 48)
            print('📍 STEP 3: Claim USDC')
            print('━' * 48)
            
            for i in range(1, Config.USDC_CLAIM_COUNT + 1):
                if await self.claim_usdc_faucet(keypair, address, i):
                    stats['usdcClaims'] += 1
            
            print(f"\n📊 USDC Claims: {stats['usdcClaims']}/{Config.USDC_CLAIM_COUNT}")
            
            # NOTE: Additional operations would be implemented here:
            # - Swap USDC to GUSD
            # - Swap GUSD to USDC
            # - Stake XAUM
            # - Redeem XAUM
            # - Deposit collateral (GR, SUI, USDC)
            # - Borrow GUSD
            # - Repay GUSD
            # - Withdraw collateral
            
            # Get final balance
            balance_after = {
                'GR': self.wallet_manager.get_token_balance(address, Config.GR_TYPE),
                'SUI': self.wallet_manager.get_token_balance(address, Config.SUI_TYPE),
                'USDC': self.wallet_manager.get_token_balance(address, Config.USDC_TYPE),
                'GUSD': self.wallet_manager.get_token_balance(address, Config.GUSD_TYPE),
                'XAUM': self.wallet_manager.get_token_balance(address, Config.XAUM_TYPE),
            }
            
            print_balance_report(address, balance_before, balance_after)
            
            print('\n✅ Wallet processed successfully!')
            stats['success'] = True
            
            return {
                'success': True,
                'stats': stats,
                'balanceBefore': balance_before,
                'balanceAfter': balance_after
            }
            
        except Exception as e:
            print(f'\n❌ Error: {str(e)}')
            
            balance_after = {
                'GR': self.wallet_manager.get_token_balance(address, Config.GR_TYPE),
                'SUI': self.wallet_manager.get_token_balance(address, Config.SUI_TYPE),
                'USDC': self.wallet_manager.get_token_balance(address, Config.USDC_TYPE),
                'GUSD': self.wallet_manager.get_token_balance(address, Config.GUSD_TYPE),
                'XAUM': self.wallet_manager.get_token_balance(address, Config.XAUM_TYPE),
            }
            
            return {
                'success': False,
                'stats': stats,
                'balanceBefore': balance_before,
                'balanceAfter': balance_after
            }
    
    async def run_daily_bot(self):
        """Main bot loop - runs once every 24 hours"""
        start_time = datetime.now()
        day_count = 1
        
        # Load proxy mappings once
        proxy_mappings = read_proxy_mappings(Config.PROXY_FILE)
        
        print(f"\n{'═' * 70}")
        print(f"  🤖 BOT WILL RUN ONCE EVERY DAY (24 HOUR LOOP)")
        print(f"  🟢 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'═' * 70}")
        print(f"  📋 PROXY CONFIGURATION LOADED")
        print(f"{'═' * 70}")
        
        for key, proxy in proxy_mappings.items():
            if proxy:
                print(f"  {key}: {proxy}")
            else:
                print(f"  {key}: LOCAL IP (empty line)")
        print()
        
        while True:
            run_start_time = datetime.now()
            print(f"\n{'═' * 70}")
            print(f"  📅 DAY #{day_count} - {run_start_time.strftime('%Y-%m-%d')}")
            print(f"  🟢 Start: {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'═' * 70}\n")
            
            # Read private keys
            private_keys = read_private_keys()
            if not private_keys:
                print('❌ No private keys found!')
                break
            
            total_stats = {
                'success': 0,
                'failed': 0,
                'xaumClaims': 0,
                'usdcClaims': 0
            }
            
            # Process all wallets
            print(f"🔄 Processing {len(private_keys)} wallets...\n")
            
            for idx, private_key in enumerate(private_keys):
                wallet = self.wallet_manager.import_wallet(private_key)
                if not wallet:
                    print(f"\n❌ Failed to import wallet #{idx + 1}\n")
                    total_stats['failed'] += 1
                    continue
                
                keypair, address = wallet
                
                # Get proxy for this wallet
                proxy_url = get_proxy_for_wallet(idx + 1, proxy_mappings)
                
                # Process wallet
                result = await self.process_wallet(
                    keypair, address, idx + 1, len(private_keys), proxy_url
                )
                
                if result['success']:
                    total_stats['success'] += 1
                else:
                    total_stats['failed'] += 1
                
                # Update stats
                for key in result['stats']:
                    if key in total_stats:
                        total_stats[key] += result['stats'][key]
                
                # Delay before next wallet
                if idx < len(private_keys) - 1:
                    await delay(get_random_delay(30, 60), 'Next wallet:')
            
            run_end_time = datetime.now()
            process_duration = int((run_end_time - run_start_time).total_seconds() / 60)
            
            # Print statistics
            print(f"\n{'═' * 70}")
            print(f"  ✅ DAY #{day_count} COMPLETED!")
            print(f"{'═' * 70}")
            print(f"  🟢 Start: {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  🔴 End: {run_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  ⏱️ Duration: {process_duration} minutes")
            print(f"{'─' * 70}")
            print('  📊 STATISTICS:')
            print(f"    🎯 Total: {len(private_keys)} | ✓ {total_stats['success']} | ✗ {total_stats['failed']}")
            print(f"    💰 XAUM: {total_stats['xaumClaims']}/{len(private_keys) * Config.XAUM_CLAIM_COUNT} | "
                  f"💵 USDC: {total_stats['usdcClaims']}/{len(private_keys) * Config.USDC_CLAIM_COUNT}")
            print(f"{'═' * 70}\n")
            
            # Calculate wait time until next day
            next_run_time = run_start_time + timedelta(days=1)
            wait_time = (next_run_time - datetime.now()).total_seconds()
            wait_hours = int(wait_time / 3600)
            wait_minutes = int((wait_time % 3600) / 60)
            
            print(f"\n{'═' * 70}")
            print(f"  ⏰ WAITING 24 HOURS UNTIL TOMORROW...")
            print(f"{'═' * 70}")
            print(f"  📅 Today: {run_start_time.strftime('%Y-%m-%d')}")
            print(f"  🔄 Next run: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  ⏱️ Wait: {wait_hours} hours {wait_minutes} minutes")
            print(f"  💤 Bot will automatically run again tomorrow")
            print(f"{'═' * 70}\n")
            
            # Wait until next day
            await delay(int(wait_time), f'Waiting until {next_run_time.strftime("%Y-%m-%d %H:%M:%S")}')
            
            day_count += 1
            print('\n' + '═' * 50)


# ============================================
# MAIN ENTRY POINT
# ============================================

async def main():
    """Main entry point"""
    print('\n🤖 AUTO BOT CREEK FINANCE - SUI TESTNET (Python Version)')
    print('📝 Rewritten in Python using pysui')
    print('⚠️ SECURITY: This is a simplified implementation for educational purposes\n')
    
    bot = CreekFinanceBot()
    
    try:
        await bot.run_daily_bot()
    except KeyboardInterrupt:
        print('\n\n⏹️ Bot stopped by user')
    except Exception as e:
        print(f'\n\n❌ Fatal Error: {str(e)}')
        raise


if __name__ == '__main__':
    asyncio.run(main())
