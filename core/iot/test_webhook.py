import requests
import json
from switchbot import query_webhook_config, set_up_webhook, delete_webhook

def test_webhook_setup():
    """Test the complete webhook setup and configuration"""
    
    # Your ngrok URL
    webhook_url = "https://00f2-142-126-181-39.ngrok-free.app"
    
    print("=== SwitchBot Webhook Testing ===")
    
    # 1. Test webhook server health
    print("\n1. Testing webhook server health...")
    try:
        health_response = requests.get(f"{webhook_url}/health")
        if health_response.status_code == 200:
            print("✅ Webhook server is healthy!")
            print(f"Response: {health_response.json()}")
        else:
            print(f"❌ Webhook server health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to webhook server: {e}")
        return False
    
    # 2. Test webhook endpoint with simulated payload
    print("\n2. Testing webhook endpoint with simulated payload...")
    try:
        test_response = requests.post(f"{webhook_url}/test")
        if test_response.status_code == 200:
            print("✅ Test webhook endpoint working!")
            print(f"Response: {test_response.json()}")
        else:
            print(f"❌ Test webhook endpoint failed: {test_response.status_code}")
    except Exception as e:
        print(f"❌ Test webhook request failed: {e}")
    
    # 3. Query current webhook configuration
    print("\n3. Querying current webhook configuration...")
    try:
        config = query_webhook_config(wh_url=webhook_url)
        print(f"Current config: {json.dumps(config, indent=2)}")
        
        if config.get('statusCode') == 100:
            print("✅ Webhook configuration found!")
        else:
            print("⚠️  No webhook configuration found or error occurred")
    except Exception as e:
        print(f"❌ Failed to query webhook config: {e}")
    
    # 4. Set up webhook if not configured
    print("\n4. Setting up webhook...")
    try:
        setup_result = set_up_webhook(wh_url=webhook_url)
        print(f"Setup result: {json.dumps(setup_result, indent=2)}")
        
        if setup_result.get('statusCode') == 100:
            print("✅ Webhook setup successful!")
        else:
            print(f"⚠️  Webhook setup may have failed: {setup_result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Failed to setup webhook: {e}")
    
    # 5. Final verification
    print("\n5. Final verification...")
    try:
        final_config = query_webhook_config(wh_url=webhook_url)
        print(f"Final config: {json.dumps(final_config, indent=2)}")
        
        if final_config.get('statusCode') == 100:
            print("✅ Webhook is properly configured and ready!")
            print("\n🎉 Testing Complete! Your webhook should now receive events from SwitchBot devices.")
            print("Try triggering your SwitchBot device to see webhook events in your server console.")
        else:
            print("❌ Webhook configuration verification failed")
    except Exception as e:
        print(f"❌ Final verification failed: {e}")
    
    return True

if __name__ == "__main__":
    test_webhook_setup() 