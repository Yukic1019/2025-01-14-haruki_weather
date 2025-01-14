from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

WEATHER_API_URL = "https://weather.tsukumijima.net/api/forecast"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def weather():
    location_id = request.args.get('location_id')
    weather_data = get_weather_data(location_id)
    return jsonify(weather_data)


def get_weather_data(location_id):
    try:
        response = requests.get(WEATHER_API_URL, params={"city": location_id})
        response.raise_for_status()  # HTTPエラーをチェック
        data = response.json()
         # forecasts が存在するか確認
        if 'forecasts' in data and data['forecasts']:
            forecast = data['forecasts'][0]
            # 風速コメントを追加
            if forecast.get('winds'):
                max_wind = float(forecast['winds'][0].get('max', 0))
                data['wind_comment'] = generate_wind_comment(max_wind)
            else:
                data['wind_comment'] = None
            
            # 最低気温と最高気温がnullの場合に対応
            if forecast.get('temperature'):
                if forecast['temperature'].get('min'):
                  if forecast['temperature']['min'].get('celsius') is None:
                    forecast['temperature']['min']['celsius'] = "不明"
                if forecast['temperature'].get('max'):
                  if forecast['temperature']['max'].get('celsius') is None:
                     forecast['temperature']['max']['celsius'] = "不明"

            #降水確率がnullの場合に対応
            if not forecast.get('chanceOfRain'):
                forecast['chanceOfRain'] = {}

        else:
            data['wind_comment'] = "情報が取得できませんでした"
            data['forecasts'] = []  # 空のリストを設定することで、HTML側でのエラーを防ぐ
            data['location'] = {
                "city": "不明"
            }
        return data
    except requests.exceptions.RequestException as e:
        print(f"エラー: 天気データの取得に失敗しました: {e}")
        return None


def generate_wind_comment(wind_speed):
    if wind_speed < 3:
        return "そよ風が心地よいですね。"
    elif wind_speed < 8:
        return "木の葉が舞い散るくらいの風です。"
    elif wind_speed < 15:
        return "傘が飛ばされそうになるくらいの風です。"
    elif wind_speed < 20:
        return "自転車が倒れるほどの風が吹いています！"
    elif wind_speed < 30:
        return "強風に注意してください！ものが飛んでくるかもしれません。"
    else:
        return "嵐のような風です。外出は控えた方が良さそうです。"

if __name__ == '__main__':
    app.run(debug=True)