"""
Direct token test - paste your token here
"""

import requests
import json

# COLE SEU TOKEN AQUI (o que funcionou no Graph API Explorer)
TOKEN = "IGAAMi315to1xBZAFNFWEJCVXZAyWWpCR3pmTlNFRHNkVEtSeWVtMzJHckNJTW0tVU5hYUFYakJOSTNlTFMwTUJhVjVYSHhiSUxZAVDA1YXFhME1tclJhcXRYRi1pbzZAvTDZAqOUlHaWlhT3daeXRIZAjRjMHd1RlNHVWgtUUJKUXV6QQZDZD"

def test_token(token):
    """Test token directly"""
    print("="*60)
    print("TESTE DIRETO DE TOKEN")
    print("="*60)
    print(f"\nToken length: {len(token)}")
    print(f"Token start: {token[:30]}...")
    print(f"Token end: ...{token[-30:]}")

    # Test 1: Me endpoint
    print("\n" + "="*60)
    print("Test 1: /me endpoint")
    print("="*60)
    url = f"https://graph.facebook.com/v24.0/me?access_token={token}"
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code != 200:
        print("\n❌ Token não funciona!")
        print("\nPossíveis causas:")
        print("1. Token expirou (tokens duram 1 hora ou 60 dias)")
        print("2. Token copiado incorretamente")
        print("3. Token não tem permissões necessárias")
        return False

    print("\n✅ Token funciona!")
    return True

if __name__ == "__main__":
    if TOKEN == "COLE_SEU_TOKEN_AQUI":
        print("⚠️  Por favor, edite este arquivo e cole seu token na variável TOKEN")
        print("\nPara obter o token:")
        print("1. Acesse: https://developers.facebook.com/tools/explorer/")
        print("2. Selecione v24.0")
        print("3. Generate Access Token")
        print("4. Copie o token completo")
        print("5. Cole neste arquivo na linha 9")
    else:
        test_token(TOKEN)
