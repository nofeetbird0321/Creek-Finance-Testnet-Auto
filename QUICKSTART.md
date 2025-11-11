# Quick Start Guide - Python Version

🚀 Get started with the Creek Finance Python bot in 3 simple steps!

## Prerequisites

- Python 3.10 or higher
- Internet connection
- SUI testnet private keys

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pysui>=0.92.0` - SUI SDK for Python
- `python-dotenv>=1.0.0` - Environment variables
- `requests>=2.31.0` - HTTP requests

## Step 2: Setup Configuration

Run the setup script to create the pysui configuration:

```bash
python setup_pysui_config.py
```

This creates `~/.pysui/PysuiConfig.json` with the testnet GraphQL endpoint.

## Step 3: Add Your Private Keys

Create a file named `privatekey.txt` in the project root:

```
suiprivkey1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
suiprivkey1qyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

⚠️ **IMPORTANT**: Never commit this file! It's already in `.gitignore`.

## Step 4: Run the Bot

```bash
python creek_bot.py
```

The bot will:
1. ✅ Check SUI balance and request faucet if needed
2. 💰 Claim XAUM tokens (3 times)
3. 💵 Claim USDC tokens (3 times)
4. 📊 Display balance reports
5. ⏰ Wait 24 hours and repeat

## Optional: Add Proxies

Create `proxy.txt` to use proxies for each wallet:

```
http://proxy1:port
http://proxy2:port

http://proxy3:port
```

- Each line = one wallet (same order as `privatekey.txt`)
- Empty line = use local IP for that wallet

## Verify It's Working

You should see output like:

```
🤖 AUTO BOT CREEK FINANCE - SUI TESTNET (Python Version)
📝 Rewritten in Python using pysui 0.92+ (GraphQL API)

╔════════════════════════════════════════════════╗
║  WALLET 1/2
╚════════════════════════════════════════════════╝
Address: 0x1234...5678
Proxy: 🌍 Local IP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 STEP 1: Check & Get SUI Balance
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💧 Ensuring wallet has minimum 1.0 SUI...
  📊 Balance: 1.234567 SUI (1/50)
  ✓ Balance sufficient!
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Profile not found in group" error
```bash
python setup_pysui_config.py
```

### "Private key file not found"
Create `privatekey.txt` and add your keys (one per line)

### Rate limiting
- Increase delays in the code
- Use proxies
- Reduce operation counts

## Configuration Options

Edit `creek_bot.py` to customize:

```python
class Config:
    MIN_SUI_BALANCE = 1.0      # Minimum SUI before faucet
    XAUM_CLAIM_COUNT = 3       # Number of XAUM claims
    USDC_CLAIM_COUNT = 3       # Number of USDC claims
    GAS_BUDGET = 200_000_000   # Gas per transaction
```

## Need Help?

- 📖 Read `README_PYTHON.md` for detailed documentation
- 🔍 Check `TEST_REPORT.md` for test results
- 🔐 Review `SECURITY_ANALYSIS.md` for security info
- 🔄 See `MIGRATION_GUIDE.md` for API details

## Security Reminders

- ⚠️ Never commit `privatekey.txt`
- ⚠️ Never share your private keys
- ⚠️ Only use on testnet
- ⚠️ Use encrypted storage in production

---

**Ready to go!** 🎉 Run `python creek_bot.py` and watch it work!
