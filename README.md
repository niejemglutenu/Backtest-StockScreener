# Backtest-StockScreener
Web application build with Django.

1. Charakterystyka oprogramowania

a. Nazwa skrócona
BacktestAPP

b. Nazwa pełna
Analytical tool for backtesting and stock screener 
Backtest&Sctockscreener

Stworzona aplikacja internetowa służy do przeprowadzania symulacji inwestycji portfelowej w akcje.
Składa się z dwóch analitycznych portali. 

A) "StockScreener" stanowi panel pozwalający na wybór konkretnej spółki giełdowej i wizualizację dostępnych danych.

B)"Backtest" stanowi panel umożliwiający przeprowadzenie analizy portfelowej na danych historycznych.
Aplikacja pozwala na zarówno użytkowanie swoich własnych danych, jak i dostarcza notowania dla wybranych spółek giełdowych. 

3. Prawa autorskie.
a. Autorzy
Miłosz Aubrecht-Prądzyński

5. Specyfikacja wymagań 
a. Wymagania zawarte

| Id  | Nazwa                  | Opis                                                                 | Priorytet  | Kategoria        |
| --- |:----------------------:|:-------------------------------------------------------------------:|:----------:|:----------------:|
| 1   | User                   | Możliwość założenia konta, funkcje logowania, rejestrowania i wylogowywania | przydatne  | funkcjonalne     |
| 2   | Pliki użytkownika       | Możliwość przetwarzania plików przesłanych przez użytkownika         | wymagane   | funkcjonalne     |
| 3   | Notowania z bazy danych | Udostępnienie użytkownikowi wybranych symboli giełdowych              | wymagane   | pozafunkcjonalne  |
| 4   | Wizualizacja danych     | Wizualizacje (wykres liniowy dla ceny, histogramy dla zwrotów, wykres świecowy) | wymagane   | funkcjonalne     |
| 5   | Opcje wizualizacji     | Wybór okresu, wykresu, symbolu | wymagane   | funkcjonalne     |
| 6    | Lista symboli           | Wyszukiwanie symbolu spółki za pomocą stale przypiętej listy         | przydatne  | funkcjonalne     |
| 7   | Przeprowadzenie testu   | Przeprowadzenie backtestu, historycznych symulacji realizacji portfeli inwestycyjnych | wymagane   | funkcjonalne     |
| 8   | Opcje backtestu     | Wybór okresu, symboli, strategii i parametrów, wysokości opłat   | wymagane   | funkcjonalne     |
| 9   | Wyniki testu            | Wyświetlenie wyników backtestu (portfolio performance metrics)       | wymagane   | pozafunkcjonalne |

b. Wymagania dodatkowe (nieosiągnięte)

| Id  | Nazwa                  | Opis                                                                 | Priorytet  | Kategoria        |
| --- |:----------------------:|:-------------------------------------------------------------------:|:----------:|:----------------:|
| 1   | Rolling window          | Podział horyzontu inwestycyjnego na określoną liczbę okien | dodatkowe  | funkcjonalne     |
| 2   | Train-validate-test      | Podział horyzontu inwestycyjnego na zestawy danych, wykorzystywanych do uczenia, walidacji i oceny jakości modeli i ich prognozy  | dodatkowe   | funkcjonalne     |
| 3   | Train-validate-test + rolling window | Połączenie dwóch powyższych funkcjonalności | dodatkowe   | funkcjonalne  |
| 4   | Strategie oparte na prognozach | Wykorzystanie informcji pochodzącej z prognozy modelu ekonometrycznego lub ML w celu budowy strategii generowania sygnałów giełdowcyh | dodatkowe   | funkcjonalne     |


6. Architektura systemu/oprogramowania



Języki:
- Python - backend
- Javasript  - frontend

Framework:
- Django==5.1.4
- Bootstrap 5.3.2 (JavaScript Bundle)

HTML:
- Django template engine
- AJAX
 
Biblioteki:
- backtrader==1.9.78.123
- pandas==2.2.3
- plotly==5.24.1

Zawarte zostały jedynie najważniejsze z wykorzystanych bibliotek. Pełna lista dostępna w requirements.txt.

7. Testy
   
a. Scenariusze testów

1) Użytkownik zakłada konto, loguje się i wylogowuje się.
2) Uzytkownik wybiera rodzaj wizualizacji oraz symbol giełdowy, a następnie wyświetla pożądane dane.
3) Uzytkownik zaznacza wszystkie niezbędne opcje testu i uruchamia backtest.
   
b. Sprawozdanie z wykonania scenariuszy testów

Każdy z testów zakończył się pozytywnie.

