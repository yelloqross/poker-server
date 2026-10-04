import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# --------------------------------------------------
# 간단한 포커 방 상태 (게임 서버 두뇌 역할)
# --------------------------------------------------
game_state = {
    "pot": 0,
    "community_cards": ["♠A", "◆K", "♥Q"],
    "player_chips": 2000,
    "bot_chips": 2000,
    "last_action": "게임을 시작합니다. 행동을 선택하세요."
}

connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. 브라우저 접속 허용
    await websocket.accept()
    connected_clients.append(websocket)
    print("📢 웹 브라우저가 접속했습니다!")

    # 접속하자마자 현재 파이썬 서버의 포커 게임 상태 전송
    await websocket.send_text(json.dumps(game_state, ensure_ascii=False))

    try:
        while True:
            # 2. 웹 화면에서 보낸 버튼 클릭 이벤트(JSON) 수신
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            action = data.get("action")
            amount = data.get("amount", 0)

            # 3. 유저 행동에 따른 파이썬 포커 로직 처리
            if action == "CALL":
                game_state["player_chips"] -= amount
                game_state["pot"] += amount
                game_state["last_action"] = f"당신이 ${amount} 콜(Call)했습니다."
            elif action == "RAISE":
                game_state["player_chips"] -= amount
                game_state["pot"] += amount
                game_state["last_action"] = f"당신이 ${amount} 레이즈(Raise)했습니다!"
            elif action == "FOLD":
                game_state["last_action"] = "당신이 폴드(Fold)했습니다. 이번 판은 봇이 승리했습니다."

            # 4. 업데이트된 최신 게임 상태를 웹 브라우저로 실시간 공유
            for client in connected_clients:
                await client.send_text(json.dumps(game_state, ensure_ascii=False))

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("📢 브라우저 연결이 종료되었습니다.")

if __name__ == "__main__":
    import uvicorn
    # 서버 실행: http://127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)