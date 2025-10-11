import asyncio
import websockets


async def test_websocket():
    uri = "ws://localhost:8029/api/v1/ws/tws-general"
    try:
        print("Tentando conectar...")
        # Connect with 10 second timeout
        websocket = await asyncio.wait_for(websockets.connect(uri), timeout=10.0)
        print("[OK] Conexao WebSocket estabelecida com sucesso!")

        # Receber mensagem de boas-vindas
        print("Aguardando mensagem de boas-vindas...")
        welcome = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        print(f"[MSG] Mensagem recebida: {welcome}")

        # Enviar mensagem sobre job em ABEND
        test_message = "qual job esta em abend?"
        print(f"Enviando mensagem: {test_message}")
        await websocket.send(test_message)
        print("[SEND] Mensagem enviada!")

        # Receber resposta
        print("Aguardando resposta do agente...")
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"[RECV] Resposta do agente: {response}")

            # Verificar se é uma resposta válida
            if '"type":"message"' in response:
                print("[SUCCESS] Resposta de mensagem recebida!")
            elif '"type":"error"' in response:
                print("[ERROR] Erro retornado pelo agente")
            else:
                print("[UNKNOWN] Resposta inesperada")

        except asyncio.TimeoutError:
            print("[TIMEOUT] Timeout - agente não respondeu (10s)")

        # Fechar conexão
        await websocket.close()
        print("[CLOSE] Conexao fechada")

    except asyncio.TimeoutError:
        print("[TIMEOUT] Timeout na conexao (10s)")
    except Exception as e:
        print(f"[CONN_ERROR] Erro de conexao: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
