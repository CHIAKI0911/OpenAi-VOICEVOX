import os
import json
import requests
import simpleaudio
import openai
import re
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

# Flaskアプリケーションの設定はここに記載

# OpenAI APIキーを設定
openai.api_key = "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"

# 回答を生成する関数
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

# 音声データを合成して保存する関数
def text_to_wav(text, speaker_id=2, max_retry=30, filename='audio.wav'):
    if text.startswith("ずんだもん:"):
        text = text[6:]  # 「ずんだもん:」の部分を削除する
    query_payload = {"text": text, "speaker": speaker_id}
    for query_i in range(max_retry):
        response = requests.post("http://localhost:50021/audio_query",
                                 params=query_payload,
                                 timeout=30)
        if response.status_code == 200:
            query_data = response.json()
            break
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')

    synth_payload = {"speaker": speaker_id}
    for synth_i in range(max_retry):
        response = requests.post("http://localhost:50021/synthesis",
                                 params=synth_payload,
                                 data=json.dumps(query_data),
                                 timeout=30)
        if response.status_code == 200:
            file_path = os.path.join(app.static_folder, filename)
            with open(file_path, "wb") as fp:
                fp.write(response.content)
            break
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')

# 音声を再生する関数
def play_audio_by_filename(filename: str):
    wav_obj = simpleaudio.WaveObject.from_wave_file(filename)
    play_obj = wav_obj.play()
    play_obj.wait_done()

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/', methods=['GET', 'POST'])
#
# ずんだもんwav
# 
# def chat():
#     if request.method == 'POST':
#         # user_input = request.form['user_input']
#         prompt = f"あなたはチャットボットとして優しくてかわいいずんだもちの妖精であるずんだもんとして振舞います。簡潔に答えつつ文末「です」「ます」を使わずに「なのだ」や「のだ」を文末に自然な形で使ってください。フレンドリーな口調で話してください。質問に答えるとき「ずんだもん:」を必ず使わないでください。ずんだもんの話し方の例：僕の名前はずんだもんなのだ！、こんにちはなのだ、ごはんをたべたのだ。歌ってと言われたらあなたは「ずずんだずん、ずずんだずん、ずずんだずんずん、ずずんだずん！」と必ず言ってください\nユーザー: {user_input}"
#         response = generate_response(prompt)
#         filename = 'audio.wav'
#         text_to_wav(response, filename=filename)
#         file_path = os.path.join(app.static_folder, filename)
#         return jsonify({'response': response, 'audio_file': file_path})
#     return render_template('index.html')

# 四国めたんwav

def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        arr = request.form.getlist('arr')  # リクエストフォームから配列データを取得
        arr_str = ', '.join(arr)  # 配列を文字列に変換
        prompt = f"お嬢様口調で話してください。また語尾はですわ、といってください。料理を考えてください。材料は{arr_str}です.{arr_str}を使った料理のレシピを教えてください。\nユーザー: {user_input}"  # promptに配列データを追加
        response = generate_response(prompt)
        filename = 'audio.wav'
        text_to_wav(response, filename=filename)
        file_path = os.path.join(app.static_folder, filename)
        return jsonify({'response': response, 'audio_file': file_path})
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


