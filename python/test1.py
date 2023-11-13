from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import openai
import subprocess
import json
import requests
import simpleaudio

app = Flask(__name__, static_folder='static')

# OpenAI APIキーを設定
openai.api_key = "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"

# 回答を生成する関数
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

# 音声データを合成して保存する関数
def text_to_wav(text, speaker_id=2, max_retry=30, filename='audio.wav'):
    query_payload = {"text":text, "speaker": speaker_id}
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
def handle_request():
    if request.method == 'POST':
        user_input = request.form['user_input']
        arr_string = request.form.get('selectedItems', '')  # デフォルト値を空文字列に設定
        arr = arr_string.split(',')
        result = chat(electedItems)
        return jsonify(result)
    return render_template('satou.html')

# chat関数内での処理
def chat(electedItems):
    arr_str = ', '.join(electedItems)
    prompt = f"{selectedItems}をの内容を表示してください."
    response = generate_response(prompt)
    filename = 'audio.wav'
    text_to_wav(response, filename=filename)
    return {'response': response, 'audio_file': filename}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')