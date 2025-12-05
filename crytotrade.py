import json
import time
import os
import sys

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

class CryptoGame:
    def __init__(self):
        self.DATA_FILE = "game_data.json"
        self.market_codes = {
            "BTC": "KRW-BTC", "ETH": "KRW-ETH", "XRP": "KRW-XRP",
            "SOL": "KRW-SOL", "DOGE": "KRW-DOGE", "ADA": "KRW-ADA",
            "ETC": "KRW-ETC", "DOT": "KRW-DOT", "TRX": "KRW-TRX",
            "AVAX": "KRW-AVAX"
        }
        self.load_game()

    def load_game(self):
        self.balance = 100000000
        self.coins = {code: 0.0 for code in self.market_codes}

        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", 100000000)
                    saved_coins = data.get("coins", {})
                    for symbol, amount in saved_coins.items():
                        if symbol in self.coins:
                            self.coins[symbol] = amount
                    return
            except Exception:
                pass

    def save_game(self):
        data = {"balance": self.balance, "coins": self.coins}
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error: {e}")

    def reset_game(self):
        print("\n⚠️ 모든 데이터를 삭제하고 초기화하시겠습니까?")
        confirm = input("초기화하려면 'y'를 입력하세요: ")
        if confirm.lower() == 'y':
            if os.path.exists(self.DATA_FILE):
                os.remove(self.DATA_FILE)
            self.balance = 100000000
            self.coins = {code: 0.0 for code in self.market_codes}
            print("\n🔄 초기화 완료! (자금 1억 원 지급)")
            self.save_game()
        else:
            print("취소되었습니다.")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_price(self, coin_symbol):
        market = self.market_codes.get(coin_symbol)
        if not market: return None
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        
        try:
            if HAS_REQUESTS:
                response = requests.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                return float(data[0]['trade_price'])
            else:
                with urllib.request.urlopen(url, timeout=3) as response:
                    data = response.read().decode('utf-8')
                    return float(json.loads(data)[0]['trade_price'])
        except Exception:
            return None

    def print_menu(self):
        mode_str = "🚀 BOOST" if HAS_REQUESTS else "🐢 BASIC"
        print("\n" + "─"*65)
        print(f"💰 [잔고: {self.balance:,.0f} KRW] | 모드: {mode_str}")
        print("1.시세 2.자산 3.매수 4.매도 5.종료 6.초기화 7.청소")
        print("─"*65)

    def show_prices(self):
        print("\n[📢 실시간 시세 Top 10]")
        for symbol in self.market_codes:
            price = self.get_price(symbol)
            if price:
                print(f"- {symbol:<5}: {price:,.0f} 원")
            else:
                print(f"- {symbol:<5}: 조회 실패")
            time.sleep(0.05)

    def show_status(self):
        print("\n[📊 자산 현황]")
        total_asset = self.balance
        has_coin = False
        
        for symbol, amount in self.coins.items():
            if amount > 0:
                has_coin = True
                price = self.get_price(symbol)
                if price:
                    val = amount * price
                    total_asset += val
                    print(f"- {symbol:<5}: {amount:.4f} 개 ({val:,.0f} 원)")
        
        if not has_coin: print("(보유 코인 없음)")
        
        profit = ((total_asset - 100000000) / 100000000) * 100
        print(f"\n💵 현금: {self.balance:,.0f} 원")
        print(f"💰 총액: {total_asset:,.0f} 원 (수익률: {profit:.2f}%)")

    def buy_coin(self):
        symbol = input("\n매수할 코인 (예: BTC, ETH, SOL) >> ").upper()
        if symbol not in self.market_codes:
            print("🚫 거래 목록에 없는 코인입니다.")
            return
        price = self.get_price(symbol)
        if not price:
            print("🚫 시세 조회 실패")
            return
            
        print(f"💎 {symbol} 현재가: {price:,.0f} 원")
        try:
            amt = int(input("매수 금액(KRW) >> "))
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
        symbol = input("\n매도할 코인 >> ").upper()
        if symbol not in self.market_codes or self.coins[symbol] <= 0:
            print("🚫 보유하지 않은 코인입니다.")
            return
        price = self.get_price(symbol)
        if not price: return
        
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
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════╗")
        print("║         💰 가상 화폐 모의투자 (Ver 2.0)              ║")
        print("╚══════════════════════════════════════════════════════╝")
        
        print("\n[시스템] 실행 환경을 점검하고 있습니다...")
        time.sleep(1)
        
        if HAS_REQUESTS:
            print("\n🚀 [시스템] 부스트 모드(Boost Mode)가 작동 중입니다!")
            print("   - 외부 라이브러리(requests)가 감지되었습니다.")
            print("   - 더 빠르고 안정적인 속도로 시세를 가져옵니다.")
        else:
            print("\n🐢 [시스템] 현재 '베이직 모드(Basic Mode)'로 실행 중입니다.")
            print("   - 표준 라이브러리(urllib)를 사용하고 있습니다.")
            print("   ----------------------------------------------------------")
            print("   💡 [TIP] 성능을 높이고 싶다면?")
            print("   터미널에 'pip install requests'를 입력해 라이브러리를 설치하세요.")
            print("   설치 후 다시 실행하면 자동으로 '부스트 모드'가 켜집니다!")
            print("   ----------------------------------------------------------")
        
        print(f"\n📂 데이터 로드 완료. (현재 잔고: {self.balance:,.0f} 원)")
        time.sleep(1)
        
        while True:
            self.print_menu()
            choice = input("선택 >> ")
            
            if choice == "1": self.show_prices()
            elif choice == "2": self.show_status()
            elif choice == "3": self.buy_coin()
            elif choice == "4": self.sell_coin()
            elif choice == "5":
                print("👋 프로그램을 종료합니다.")
                break
            elif choice == "6": self.reset_game()
            elif choice == "7": 
                self.clear_screen()
                print("✨ 화면이 깨끗해졌습니다.")
            else: print("🚫 잘못된 입력입니다.")

if __name__ == "__main__":
    game = CryptoGame()
    game.run()