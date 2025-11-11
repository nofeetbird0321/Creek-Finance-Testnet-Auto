#!/usr/bin/env python3
"""
Setup script for pysui 0.92+ configuration

This script creates the necessary configuration file for pysui 0.92+ GraphQL client.
Run this before using creek_bot.py for the first time.
"""

import json
import os
from pathlib import Path


def create_pysui_config():
    """Create minimal pysui configuration for GraphQL testnet"""
    
    config_dir = Path.home() / ".pysui"
    config_path = config_dir / "PysuiConfig.json"
    
    # Check if config already exists
    if config_path.exists():
        print(f"⚠️  Configuration already exists at: {config_path}")
        response = input("Do you want to overwrite it? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Setup cancelled")
            return False
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Creating config directory: {config_dir}")
    
    # Create pysui configuration structure
    # Based on pysui 0.92+ requirements
    config_data = {
        "version": "1.1.0",
        "sui_binary": "",
        "group_active": "sui_gql_config",
        "groups": [
            {
                "group_name": "sui_gql_config",
                "using_profile": "testnet",
                "using_address": "",
                "alias_list": [],
                "key_list": [],
                "address_list": [],
                "profiles": [
                    {
                        "profile_name": "testnet",
                        "url": "https://sui-testnet.mystenlabs.com/graphql",
                        "faucet_url": "https://faucet.testnet.sui.io/v2/gas"
                    }
                ],
                "protocol": 1  # 1 = GRAPHQL, 2 = GRPC, 3 = OTHER
            }
        ]
    }
    
    # Write config
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"✅ Created pysui configuration at: {config_path}")
    print("\n📝 Configuration details:")
    print(f"   Active group: {config_data['group_active']}")
    print(f"   GraphQL group: {config_data['groups'][0]['group_name']}")
    print("\n✅ Setup complete! You can now run creek_bot.py")
    
    return True


def main():
    """Main entry point"""
    print("\n🔧 pysui 0.92+ Configuration Setup")
    print("=" * 50)
    print("This script will create the pysui configuration")
    print("needed for GraphQL client in pysui 0.92+")
    print("=" * 50)
    print()
    
    try:
        if create_pysui_config():
            print("\n🎉 Success! You're ready to use creek_bot.py")
        else:
            print("\n❌ Setup was not completed")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
