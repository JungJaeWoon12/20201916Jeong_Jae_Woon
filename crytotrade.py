import urllib.request
import json
import time
import os

class CryptoGame:
    def __init__(self):
        self.DATA_FILE = "game_data.json"
        self.market_codes = {
            "BTC": "KRW-BTC",
            "ETH": "KRW-ETH",
            "XRP": "KRW-XRP"
        }
        self.load_game()

    def load_game(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.balance = data["balance"]
                    self.coins = data["coins"]
                    print(f"📂 저장된 게임 데이터를 불러왔습니다. (잔고: {self.balance:,.0f}원)")
                    return
            except Exception:
                pass
        self.balance = 10000000
        self.coins = {"BTC": 0.0, "ETH": 0.0, "XRP": 0.0}

    def save_game(self):
        data = {"balance": self.balance, "coins": self.coins}
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"저장 실패: {e}")

    def reset_game(self):
        print("\n⚠️ 정말로 모든 데이터를 삭제하고 처음으로 돌아가시겠습니까?")
        confirm = input("초기화하려면 'y'를 입력하세요: ")
        if confirm.lower() == 'y':
            if os.path.exists(self.DATA_FILE):
                os.remove(self.DATA_FILE)
            self.balance = 10000000
            self.coins = {"BTC": 0.0, "ETH": 0.0, "XRP": 0.0}
            print("\n🔄 게임이 초기화되었습니다!")
            self.save_game()
        else:
            print("취소되었습니다.")

    def clear_screen(self):
        """화면을 깨끗하게 지우는 함수"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_price(self, coin_symbol):
        market = self.market_codes.get(coin_symbol)
        if not market: return None
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        try:
            response = urllib.request.urlopen(url)
            data = response.read().decode('utf-8')
            return float(json.loads(data)[0]['trade_price'])
        except Exception:
            return None

    def print_menu(self):
        print("\n" + "─"*60)
        # 메뉴에 7번 청소 기능이 추가되었습니다.
        print(f"💰 [잔고: {self.balance:,.0f} KRW] | 1.시세 2.자산 3.매수 4.매도 5.종료 6.초기화 7.청소")
        print("─"*60)

    def show_prices(self):
        print("\n[📢 실시간 시세]")
        for symbol in self.market_codes:
            price = self.get_price(symbol)
            if price:
                print(f"- {symbol}: {price:,.0f} 원")
            time.sleep(0.1)

    def show_status(self):
        print("\n[📊 내 자산 현황]")
        total_asset = self.balance
        for symbol, amount in self.coins.items():
            if amount > 0:
                price = self.get_price(symbol)
                val = amount * price
                total_asset += val
                print(f"- {symbol}: {amount:.4f} 개 ({val:,.0f} 원)")
        
        profit = ((total_asset - 10000000) / 10000000) * 100
        print(f"💵 현금: {self.balance:,.0f} 원")
        print(f"💰 총액: {total_asset:,.0f} 원 (수익률: {profit:.2f}%)")

    def buy_coin(self):
        self.show_prices()
        symbol = input("\n매수 코인(BTC/ETH/XRP) >> ").upper()
        if symbol not in self.market_codes:
            print("🚫 코인명을 확인하세요.")
            return
        price = self.get_price(symbol)
        try:
            amt = int(input(f"{symbol} 매수 금액(KRW) >> "))
            if amt > self.balance: print("🚫 잔액 부족")
            elif amt <= 0: print("🚫 금액 오류")
            else:
                cnt = amt / price
                self.balance -= amt
                self.coins[symbol] += cnt
                print(f"✅ {symbol} {cnt:.4f}개 매수 완료!")
                self.save_game()
        except ValueError: print("🚫 숫자만 입력하세요.")

    def sell_coin(self):
        self.show_status()
        symbol = input("\n매도 코인(BTC/ETH/XRP) >> ").upper()
        if symbol not in self.market_codes or self.coins[symbol] <= 0:
            print("🚫 보유 코인이 아닙니다.")
            return
        price = self.get_price(symbol)
        try:
            pct = int(input("매도 비율(1~100%) >> "))
            if 1 <= pct <= 100:
                cnt = self.coins[symbol] * (pct / 100)
                val = cnt * price
                self.coins[symbol] -= cnt
                self.balance += val
                print(f"✅ {symbol} {cnt:.4f}개 매도 완료! (+{val:,.0f} 원)")
                self.save_game()
            else: print("🚫 1~100 사이 입력")
        except ValueError: print("🚫 숫자만 입력하세요.")

    def run(self):
        self.clear_screen() # 처음 시작할 때는 깔끔하게
        print("🚀 무설치 코인 투자 게임 (History Mode)")
        
        while True:
            self.print_menu()
            choice = input("선택 >> ")
            
            if choice == "1": self.show_prices()
            elif choice == "2": self.show_status()
            elif choice == "3": self.buy_coin()
            elif choice == "4": self.sell_coin()
            elif choice == "5":
                print("👋 게임을 종료합니다.")
                break
            elif choice == "6": self.reset_game()
            elif choice == "7": 
                self.clear_screen() # 7번을 누르면 화면을 싹 지웁니다.
                print("✨ 화면이 깨끗해졌습니다.") 
            else: print("🚫 잘못된 입력입니다.")

if __name__ == "__main__":
    game = CryptoGame()
    game.run()