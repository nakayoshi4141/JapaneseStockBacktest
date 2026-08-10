# JapaneseStockBacktest Version 1.0.1 Final

日産自動車（7201）の日足CSVを対象とする日本株バックテストです。
Python 3.11、GitHub、Google Colabでの利用を想定しています。

## 固定仕様
- 初期資金: 5,000,000円（`config.py`で変更可能）
- 初回購入: 100株（変更可能）
- ナンピン: 直前購入価格から6%下落した価格で購入（変更可能）
- 最大購入回数: 10回（初回購入を含む、変更可能）
- 利確: 平均取得価格から3%上昇した価格で全株売却（変更可能）
- 手数料・税金: Version 1.0.1では考慮しない
- CSV列名: `日付, 始値, 高値, 安値, 終値`

初回購入は始値で行い、その同一営業日の高値が利確条件に達した場合も利確判定を行います。

保有中の同一営業日の高値と安値の両方が条件に達する場合、利確判定を先に行います。
これはOHLCだけでは日中の価格順序を特定できないため、バックテスト上の固定ルールです。

## 実行
```bash
pip install -r requirements.txt
python main.py
```

Google Colabではリポジトリをクローンして同じコマンドを実行できます。

## 出力
`output/BacktestResult.xlsx`
`output/trade_history.csv`
`output/equity_curve.png`
