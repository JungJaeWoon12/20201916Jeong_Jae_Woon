import urllib.request
import json
import time
import os
import sys

class CryptoGame:
    def __init__(self):
        # 게임 초기 설정
        self.balance = 10000000  # 초기 자금 1,000만원
        self.coins = {           # 보유 코인 현황
            "BTC": 0.0,
            "ETH": 0.0,
            "XRP": 0.0
        }
        # 업비트 API 마켓 코드 (별도 인증 키 필요 없음)
        self.market_codes = {
            "BTC": "KRW-BTC",
            "ETH": "KRW-ETH",
            "XRP": "KRW-XRP"
        }

    def clear_screen(self):
        # 화면 지우기 (윈도우/맥 호환)
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_price(self, coin_symbol):
        """
        외부 라이브러리(requests) 없이 urllib만 사용하여 시세 조회
        """
        market = self.market_codes.get(coin_symbol)
        if not market:
            return None
            
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        
        try:
            # 1. 웹 요청 (내장 라이브러리)
            response = urllib.request.urlopen(url)
            # 2. 데이터 읽기 및 디코딩
            data = response.read().decode('utf-8')
            # 3. JSON 변환
            json_data = json.loads(data)
            # 4. 현재가 추출
            return float(json_data[0]['trade_price'])
        except Exception as e:
            print(f"[시스템] 시세 조회 중 오류 발생: {e}")
            return None

    def print_menu(self):
        print("\n" + "="*30)
        print(f"💰 현재 잔고: {self.balance:,.0f} KRW")
        print("="*30)
        print("1. 📈 실시간 시세 조회")
        print("2. 💎 내 자산 현황 (수익률)")
        print("3. 🛒 코인 매수")
        print("4. 💸 코인 매도")
        print("5. 🚪 게임 종료")
        print("="*30)

    def show_prices(self):
        print("\n[📢 실시간 시세]")
        for symbol in self.market_codes:
            price = self.get_price(symbol)
            if price:
                print(f"- {symbol}: {price:,.0f} 원")
            time.sleep(0.1) # API 요청 과부하 방지

    def show_status(self):
        print("\n[📊 내 자산 현황]")
        total_asset = self.balance
        
        for symbol, amount in self.coins.items():
            if amount > 0:
                current_price = self.get_price(symbol)
                value = amount * current_price
                total_asset += value
                print(f"- {symbol}: {amount:.4f} 개 (평가액: {value:,.0f} 원)")
        
        print(f"\n💵 현금 잔고: {self.balance:,.0f} 원")
        print(f"💰 총 자산 가치: {total_asset:,.0f} 원")
        
        # 수익률 계산
        profit_rate = ((total_asset - 10000000) / 10000000) * 100
        print(f"📈 수익률: {profit_rate:.2f}%")

    def buy_coin(self):
        self.show_prices()
        symbol = input("\n매수할 코인을 입력하세요 (BTC/ETH/XRP): ").upper()
        if symbol not in self.market_codes:
            print("🚫 잘못된 코인명입니다.")
            return

        current_price = self.get_price(symbol)
        print(f"\n{symbol} 현재가: {current_price:,.0f} 원")
        
        try:
            amount_krw = int(input("매수할 금액(KRW)을 입력하세요: "))
            if amount_krw > self.balance:
                print("🚫 잔액이 부족합니다.")
            elif amount_krw <= 0:
                print("🚫 금액을 정확히 입력해주세요.")
            else:
                buy_amount = amount_krw / current_price
                self.balance -= amount_krw
                self.coins[symbol] += buy_amount
                print(f"✅ {symbol} {buy_amount:.4f}개 매수 완료!")
        except ValueError:
            print("🚫 숫자로만 입력해주세요.")

    def sell_coin(self):
        self.show_status()
        symbol = input("\n매도할 코인을 입력하세요 (BTC/ETH/XRP): ").upper()
        if symbol not in self.market_codes or self.coins[symbol] <= 0:
            print("🚫 보유하고 있지 않거나 잘못된 코인명입니다.")
            return

        current_price = self.get_price(symbol)
        max_sell = self.coins[symbol]
        print(f"\n보유량: {max_sell:.4f} {symbol} (평가액: {max_sell*current_price:,.0f} 원)")

        try:
            percent = int(input("매도할 비율을 입력하세요 (1~100%): "))
            if 1 <= percent <= 100:
                sell_amount = max_sell * (percent / 100)
                sell_value = sell_amount * current_price
                
                self.coins[symbol] -= sell_amount
                self.balance += sell_value
                print(f"✅ {symbol} {sell_amount:.4f}개 매도 완료! (+{sell_value:,.0f} 원)")
            else:
                print("🚫 1에서 100 사이의 숫자를 입력하세요.")
        except ValueError:
            print("🚫 숫자로만 입력해주세요.")

    def run(self):
        self.clear_screen()
        print("🚀 가상 화폐 모의투자 게임에 오신 것을 환영합니다!")
        time.sleep(1)
        
        while True:
            self.print_menu()
            choice = input("선택 >> ")
            
            if choice == "1":
                self.show_prices()
            elif choice == "2":
                self.show_status()
            elif choice == "3":
                self.buy_coin()
            elif choice == "4":
                self.sell_coin()
            elif choice == "5":
                print("게임을 종료합니다. 성투하세요! 👋")
                break
            else:
                print("🚫 잘못된 입력입니다.")
            
            input("\n[엔터를 누르면 메뉴로 돌아갑니다]")
            self.clear_screen()

if __name__ == "__main__":
    game = CryptoGame()
    game.run()