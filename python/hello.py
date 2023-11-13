import json
import requests
import simpleaudio
import openai

# OpenAI APIキーを設定
openai.api_key = "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"

def generate_response(prompt):
    # OpenAI Chat APIを使用して回答を生成
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,
        temperature=0.7,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

def text_to_wav(text, speaker_id=3, max_retry=20, filename='audio.wav'):
    # Voicevoxサーバーにリクエストを送信して音声データを取得
    query_payload = {"text": text, "speaker": speaker_id}
    for query_i in range(max_retry):
        response = requests.post("http://localhost:50021/audio_query",
                                 params=query_payload,
                                 timeout=10)
        if response.status_code == 200:
            query_data = response.json()
            break
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')

    # 音声データを合成してwavファイルに保存
    synth_payload = {"speaker": speaker_id}
    for synth_i in range(max_retry):
        response = requests.post("http://localhost:50021/synthesis",
                                 params=synth_payload,
                                 data=json.dumps(query_data),
                                 timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as fp:
                fp.write(response.content)
            break
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')


def play_audio_by_filename(filename: str):
    # 保存したwavファイルを再生
    wav_obj = simpleaudio.WaveObject.from_wave_file(filename)
    play_obj = wav_obj.play()
    play_obj.wait_done()


if __name__ == '__main__':
    filename = 'audio.wav'  # 音声データのファイル名

    # ユーザーの入力を取得
    user_input = input("質問を入力してください: ")

    # OpenAIにユーザーの入力を渡して回答を生成
    prompt = f"あなたは賢いAIとして簡潔に答えてください\nユーザー: {user_input}"
    response = generate_response(prompt)

    # 回答を音声合成してwavファイルに保存
    text_to_wav(response, filename=filename)

    # 保存したwavファイルを再生
    play_audio_by_filename(filename)
