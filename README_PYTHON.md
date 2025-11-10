# Creek Finance Automation Bot - Python Version

🤖 Python implementation of Creek Finance Testnet automation bot using **pysui**

## ⚠️ IMPORTANT SECURITY NOTES

This Python version implements the same functionality as the JavaScript version but with improved security considerations:

1. **Private Key Storage**: Keys are still read from plain text files. For production:
   - Use environment variables
   - Use encrypted key storage (e.g., keyring, AWS Secrets Manager)
   - Use hardware wallets for production environments

2. **Rate Limiting**: Improved handling with configurable cooldown periods

3. **Error Handling**: More robust error handling and recovery

4. **Logging**: Structured logging without exposing sensitive data

## 🚀 Features

- ✅ Auto faucet management (SUI, XAUM, USDC)
- ✅ Token swaps (USDC ↔ GUSD)
- ✅ Staking and redeeming XAUM
- ✅ Lending protocol operations (deposit, borrow, repay, withdraw)
- ✅ Health factor monitoring and management
- ✅ 24-hour daily scheduler
- ✅ Multi-wallet support
- ✅ Proxy support for each wallet

## ⚙️ Requirements

### System Requirements
- Python 3.8 or higher
- Internet connection
- SUI Testnet account(s)

### Python Dependencies
Install required packages:

```bash
pip install -r requirements.txt
```

Dependencies:
- `pysui>=0.65.0` - SUI SDK for Python
- `python-dotenv>=1.0.0` - Environment variable management
- `requests>=2.31.0` - HTTP requests

## 📁 File Structure

```
Creek-Finance-Testnet-Auto/
├── creek_bot.py          # Main Python bot script
├── requirements.txt      # Python dependencies
├── privatekey.txt        # Your wallet private keys (DO NOT COMMIT!)
├── proxy.txt            # Optional proxy configuration
├── .gitignore           # Git ignore file (includes privatekey.txt)
├── README_PYTHON.md     # This file
└── SECURITY_ANALYSIS.md # Security vulnerability report
```

## 🔧 Configuration

### 1. Private Keys
Create a `privatekey.txt` file with your private keys (one per line):

```
suiprivkey1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
suiprivkey1qyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

**SECURITY WARNING**: Never commit this file to Git! It's already in `.gitignore`.

### 2. Proxy Configuration (Optional)
Create a `proxy.txt` file to assign proxies to wallets:

```
http://proxy1:port
http://proxy2:port

http://proxy3:port
```

- Each line corresponds to a wallet in the same order as `privatekey.txt`
- Empty lines = use local IP for that wallet
- Lines starting with `#` are comments

## 🏃 Running the Bot

### Basic Usage

```bash
python creek_bot.py
```

### Run in Background (Linux/Mac)

```bash
nohup python creek_bot.py > bot.log 2>&1 &
```

### Run with Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python creek_bot.py
```

## 📊 Configuration Options

Edit the `Config` class in `creek_bot.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_SUI_BALANCE` | 1.0 | Minimum SUI balance before requesting faucet |
| `XAUM_CLAIM_COUNT` | 3 | Number of XAUM claims per cycle |
| `USDC_CLAIM_COUNT` | 3 | Number of USDC claims per cycle |
| `STAKE_XAUM_COUNT` | 3 | Number of staking operations |
| `DEPOSIT_GR_COUNT` | 3 | Number of GR deposits |
| `BORROW_GUSD_COUNT` | 3 | Number of GUSD borrow operations |
| `GAS_BUDGET` | 200000000 | Gas budget per transaction |

## 🔐 Security Best Practices

### 1. Private Key Management
```python
# ❌ BAD: Plain text file
with open('privatekey.txt') as f:
    keys = f.read()

# ✅ BETTER: Environment variables
import os
private_key = os.environ.get('SUI_PRIVATE_KEY')

# ✅ BEST: Encrypted storage or hardware wallet
from keyring import get_password
private_key = get_password('creek_bot', 'wallet1')
```

### 2. Use `.env` File (Recommended)
```bash
# .env file
SUI_PRIVATE_KEY_1=suiprivkey1qxxx...
SUI_PRIVATE_KEY_2=suiprivkey1qyyy...
```

```python
# In your code
from dotenv import load_dotenv
load_dotenv()

keys = [
    os.getenv('SUI_PRIVATE_KEY_1'),
    os.getenv('SUI_PRIVATE_KEY_2')
]
```

### 3. Never Commit Secrets
Ensure `.gitignore` includes:
```
privatekey.txt
proxy.txt
.env
*.key
```

### 4. Use Read-Only Keys Where Possible
For monitoring operations, consider using read-only API keys.

### 5. Run on Secure Infrastructure
- Use dedicated servers
- Enable firewall rules
- Use VPN for sensitive operations
- Monitor for suspicious activity

## 🐛 Troubleshooting

### Module Not Found
```bash
pip install -r requirements.txt
```

### Private Key File Not Found
```bash
# Check if file exists
ls -la privatekey.txt

# Create if missing
touch privatekey.txt
# Then add your keys
```

### Rate Limiting
If you get rate limited:
- Increase delays between operations
- Use proxies (configure in `proxy.txt`)
- Reduce operation counts in Config

### Transaction Failures
- Check gas budget is sufficient
- Verify contract addresses are correct
- Check wallet has enough balance
- Review transaction logs

## 📝 Implementation Status

### ✅ Implemented
- Configuration management
- Wallet management and key import
- SUI balance checking and faucet requests
- XAUM and USDC faucet claims
- Health factor calculation
- Balance tracking and reporting
- 24-hour scheduling loop
- Proxy support
- Error handling

### 🚧 To Be Implemented
The following features from the JavaScript version need full implementation:

1. **Swap Operations**
   - USDC → GUSD swap
   - GUSD → USDC swap

2. **Staking Operations**
   - Stake XAUM tokens
   - Redeem/unstake XAUM

3. **Lending Protocol**
   - Deposit collateral (GR, SUI, USDC)
   - Create obligation
   - Borrow GUSD
   - Repay GUSD
   - Withdraw collateral

4. **Price Oracle Updates**
   - Fetch real-time prices
   - Update price oracle

These require deeper integration with pysui's transaction builder and Move call functionality.

## 🔄 Migration from JavaScript

### Key Differences

1. **Async/Await**
   - JavaScript: Native async/await
   - Python: Uses `asyncio` library

2. **Transaction Building**
   - JavaScript: `TransactionBlock` from `@mysten/sui.js`
   - Python: `SyncTransaction` from `pysui`

3. **Error Handling**
   - JavaScript: Try-catch with `.status.status`
   - Python: Try-except with `.is_ok()`

4. **Client Initialization**
   - JavaScript: `new SuiClient({ url })`
   - Python: `SyncClient(SuiConfig)`

### API Mapping

| JavaScript | Python |
|------------|--------|
| `suiClient.getBalance()` | `client.get_gas()` |
| `suiClient.getCoins()` | `client.get_coin()` |
| `TransactionBlock()` | `SyncTransaction()` |
| `tx.moveCall()` | `txn.move_call()` |
| `signAndExecuteTransactionBlock()` | `txn.execute()` |

## 📚 Additional Resources

- [pysui Documentation](https://pysui.readthedocs.io/)
- [SUI Documentation](https://docs.sui.io/)
- [Creek Finance](https://creek.finance/)
- [SUI Testnet Faucet](https://faucet.testnet.sui.io/)

## ⚖️ License

MIT License - Use at your own risk

## ⚠️ Disclaimer

This bot is for educational purposes only. Use on testnet only. Never use with real funds unless you fully understand the risks. The authors are not responsible for any losses incurred from using this software.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review `SECURITY_ANALYSIS.md`
- Open an issue on GitHub

---

**Remember**: Always test on testnet first! Never expose private keys! Use at your own risk!
